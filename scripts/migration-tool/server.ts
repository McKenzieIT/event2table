#!/usr/bin/env tsx
/**
 * Migration Tool Server
 * 
 * WebSocket server that provides AST transformation services
 * for the visual migration tool.
 * 
 * @usage
 *   npx tsx scripts/migration-tool/server.ts --port 3001
 */

import * as http from 'http';
import * as fs from 'fs';
import * as path from 'path';
import { WebSocketServer, WebSocket } from 'ws';
import { parse } from '@babel/parser';
import traverse from '@babel/traverse';
import generate from '@babel/generator';
import * as t from '@babel/types';
import {
  MigrationMessage,
  FileInfo,
  ChangeInfo,
  RuleInfo,
  TransformResult
} from './websocket';

// ========================================
// Server Configuration
// ========================================

interface ServerConfig {
  port: number;
  host: string;
  rootDir: string;
  backupDir: string;
}

const defaultConfig: ServerConfig = {
  port: 3001,
  host: 'localhost',
  rootDir: process.cwd(),
  backupDir: 'scripts/.migration-backups'
};

// ========================================
// Transformation Rules
// ========================================

const transformationRules: RuleInfo[] = [
  {
    id: 'modal-to-basemodal',
    name: 'Modal to BaseModal',
    description: 'Migrates Modal component to new BaseModal API',
    componentPattern: 'Modal',
    enabled: true
  },
  {
    id: 'table-migration',
    name: 'Table Migration',
    description: 'Migrates Table component to new API',
    componentPattern: 'Table',
    enabled: true
  },
  {
    id: 'form-migration',
    name: 'Form Migration',
    description: 'Migrates Form component to new API',
    componentPattern: 'Form',
    enabled: true
  },
  {
    id: 'select-migration',
    name: 'Select Migration',
    description: 'Migrates Select component to new API',
    componentPattern: 'Select',
    enabled: true
  }
];

// ========================================
// Migration Server Class
// ========================================

class MigrationServer {
  private server: http.Server;
  private wss: WebSocketServer;
  private config: ServerConfig;
  private backupManifest: Map<string, string> = new Map();

  constructor(config: Partial<ServerConfig> = {}) {
    this.config = { ...defaultConfig, ...config };
    this.server = http.createServer();
    this.wss = new WebSocketServer({ server: this.server });
    this.setupWebSocket();
  }

  private setupWebSocket(): void {
    this.wss.on('connection', (ws: WebSocket) => {
      console.log('Client connected');

      ws.on('message', (data: Buffer) => {
        try {
          const message: MigrationMessage = JSON.parse(data.toString());
          this.handleMessage(ws, message);
        } catch (error) {
          console.error('Failed to parse message:', error);
          this.sendError(ws, 'PARSE_ERROR', 'Failed to parse message');
        }
      });

      ws.on('close', () => {
        console.log('Client disconnected');
      });

      ws.on('error', (error) => {
        console.error('WebSocket error:', error);
      });
    });
  }

  private async handleMessage(ws: WebSocket, message: MigrationMessage): Promise<void> {
    switch (message.type) {
      case 'file:list:request':
        await this.handleFileList(ws, message);
        break;
      case 'transform:request':
        await this.handleTransform(ws, message);
        break;
      case 'batch:request':
        await this.handleBatchTransform(ws, message);
        break;
      case 'rollback:request':
        await this.handleRollback(ws, message);
        break;
      case 'rule:list:request':
        this.handleRuleList(ws, message);
        break;
      default:
        this.sendError(ws, 'UNKNOWN_MESSAGE', `Unknown message type: ${(message as any).type}`);
    }
  }

  // ========================================
  // Message Handlers
  // ========================================

  private async handleFileList(ws: WebSocket, message: MigrationMessage): Promise<void> {
    const request = message as any;
    const directory = request.directory || this.config.rootDir;

    try {
      const files = await this.scanDirectory(directory);
      const response: MigrationMessage = {
        type: 'file:list:response',
        timestamp: Date.now(),
        id: message.id,
        files
      };
      this.send(ws, response);
    } catch (error) {
      this.sendError(ws, 'FILE_LIST_ERROR', `Failed to list files: ${error}`);
    }
  }

  private async handleTransform(ws: WebSocket, message: MigrationMessage): Promise<void> {
    const request = message as any;
    const { filePath, rules, preview } = request;

    try {
      const result = await this.transformFile(filePath, rules, preview);
      const response: MigrationMessage = {
        type: 'transform:response',
        timestamp: Date.now(),
        id: message.id,
        ...result
      };
      this.send(ws, response);
    } catch (error) {
      this.sendError(ws, 'TRANSFORM_ERROR', `Transform failed: ${error}`);
    }
  }

  private async handleBatchTransform(ws: WebSocket, message: MigrationMessage): Promise<void> {
    const request = message as any;
    const { directory, rules, dryRun } = request;

    try {
      const files = await this.scanDirectory(directory);
      const results: TransformResult[] = [];
      let totalChanges = 0;

      for (let i = 0; i < files.length; i++) {
        const file = files[i];

        // Send progress update
        const progressMsg: MigrationMessage = {
          type: 'batch:progress',
          timestamp: Date.now(),
          id: message.id,
          totalFiles: files.length,
          processedFiles: i,
          currentFile: file.path,
          status: 'processing',
          changes: totalChanges
        };
        this.send(ws, progressMsg);

        // Transform file
        const result = await this.transformFile(file.path, rules, dryRun);
        results.push({
          filePath: file.path,
          success: result.success,
          changes: result.changes.length,
          warnings: result.warnings.length,
          errors: result.errors.length
        });
        totalChanges += result.changes.length;
      }

      // Send completion message
      const completeMsg: MigrationMessage = {
        type: 'batch:complete',
        timestamp: Date.now(),
        id: message.id,
        totalFiles: files.length,
        successfulFiles: results.filter(r => r.success).length,
        failedFiles: results.filter(r => !r.success).length,
        totalChanges,
        duration: 0,
        results
      };
      this.send(ws, completeMsg);
    } catch (error) {
      this.sendError(ws, 'BATCH_ERROR', `Batch transform failed: ${error}`);
    }
  }

  private async handleRollback(ws: WebSocket, message: MigrationMessage): Promise<void> {
    const request = message as any;
    const filePath = request.filePath;

    try {
      const rolledBackFiles: string[] = [];

      if (filePath) {
        // Rollback specific file
        if (this.backupManifest.has(filePath)) {
          await this.rollbackFile(filePath);
          rolledBackFiles.push(filePath);
        }
      } else {
        // Rollback all files
        for (const [path] of this.backupManifest) {
          await this.rollbackFile(path);
          rolledBackFiles.push(path);
        }
      }

      const response: MigrationMessage = {
        type: 'rollback:response',
        timestamp: Date.now(),
        id: message.id,
        success: true,
        rolledBackFiles
      };
      this.send(ws, response);
    } catch (error) {
      this.sendError(ws, 'ROLLBACK_ERROR', `Rollback failed: ${error}`);
    }
  }

  private handleRuleList(ws: WebSocket, message: MigrationMessage): void {
    const response: MigrationMessage = {
      type: 'rule:list:response',
      timestamp: Date.now(),
      id: message.id,
      rules: transformationRules
    };
    this.send(ws, response);
  }

  // ========================================
  // Core Operations
  // ========================================

  private async scanDirectory(directory: string): Promise<FileInfo[]> {
    const files: FileInfo[] = [];

    const walk = (currentPath: string) => {
      try {
        const entries = fs.readdirSync(currentPath, { withFileTypes: true });

        for (const entry of entries) {
          const fullPath = path.join(currentPath, entry.name);

          if (entry.isDirectory()) {
            if (!['node_modules', '.git', 'dist', 'build'].includes(entry.name)) {
              walk(fullPath);
            }
          } else if (entry.isFile()) {
            const ext = path.extname(entry.name);
            if (['.ts', '.tsx'].includes(ext)) {
              const stat = fs.statSync(fullPath);
              files.push({
                path: fullPath,
                name: entry.name,
                extension: ext,
                size: stat.size,
                lastModified: stat.mtime.getTime(),
                hasMigration: this.checkMigration(fullPath),
                migrationType: this.getMigrationType(fullPath)
              });
            }
          }
        }
      } catch (error) {
        console.error(`Error scanning directory ${currentPath}:`, error);
      }
    };

    walk(directory);
    return files;
  }

  private checkMigration(filePath: string): boolean {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      return content.includes('@/components/Modal') ||
             content.includes('@/components/Table') ||
             content.includes('@/components/Form') ||
             content.includes('@/components/Select');
    } catch {
      return false;
    }
  }

  private getMigrationType(filePath: string): string | undefined {
    try {
      const content = fs.readFileSync(filePath, 'utf-8');
      if (content.includes('@/components/Modal')) return 'Modal';
      if (content.includes('@/components/Table')) return 'Table';
      if (content.includes('@/components/Form')) return 'Form';
      if (content.includes('@/components/Select')) return 'Select';
      return undefined;
    } catch {
      return undefined;
    }
  }

  private async transformFile(
    filePath: string,
    rules: string[],
    preview: boolean
  ): Promise<{
    filePath: string;
    success: boolean;
    changes: ChangeInfo[];
    warnings: string[];
    errors: string[];
    originalCode: string;
    transformedCode: string;
  }> {
    const result = {
      filePath,
      success: false,
      changes: [] as ChangeInfo[],
      warnings: [] as string[],
      errors: [] as string[],
      originalCode: '',
      transformedCode: ''
    };

    try {
      const code = fs.readFileSync(filePath, 'utf-8');
      result.originalCode = code;

      const ast = parse(code, {
        sourceType: 'module',
        plugins: ['typescript', 'jsx', 'decorators-legacy'],
        allowImportExportEverywhere: true,
        errorRecovery: true
      });

      // Apply transformations
      traverse(ast, {
        ImportDeclaration: (traversePath) => {
          const source = traversePath.node.source.value;
          
          // Modal migration
          if (rules.includes('modal-to-basemodal') && source === '@/components/Modal') {
            traversePath.node.source.value = '@shared/ui/BaseModal/BaseModal';
            result.changes.push({
              type: 'import',
              description: 'Modal import path updated',
              before: '@/components/Modal',
              after: '@shared/ui/BaseModal/BaseModal'
            });
          }

          // Table migration
          if (rules.includes('table-migration') && source === '@/components/Table') {
            traversePath.node.source.value = '@shared/ui/Table';
            result.changes.push({
              type: 'import',
              description: 'Table import path updated',
              before: '@/components/Table',
              after: '@shared/ui/Table'
            });
          }

          // Form migration
          if (rules.includes('form-migration') && source === '@/components/Form') {
            traversePath.node.source.value = '@shared/ui/components/Form';
            result.changes.push({
              type: 'import',
              description: 'Form import path updated',
              before: '@/components/Form',
              after: '@shared/ui/components/Form'
            });
          }

          // Select migration
          if (rules.includes('select-migration') && source === '@/components/Select') {
            traversePath.node.source.value = '@shared/ui/components/Select';
            result.changes.push({
              type: 'import',
              description: 'Select import path updated',
              before: '@/components/Select',
              after: '@shared/ui/components/Select'
            });
          }
        },
        JSXOpeningElement: (traversePath) => {
          if (!t.isJSXIdentifier(traversePath.node.name)) return;

          const componentName = traversePath.node.name.name;

          // Modal to BaseModal
          if (rules.includes('modal-to-basemodal') && componentName === 'Modal') {
            traversePath.node.name.name = 'BaseModal';
            result.changes.push({
              type: 'component',
              description: 'Component renamed',
              before: 'Modal',
              after: 'BaseModal'
            });
          }
        }
      });

      // Generate transformed code
      const output = generate(ast, {
        retainLines: false,
        compact: false
      });
      result.transformedCode = output.code;

      // Create backup and write if not preview
      if (!preview && result.changes.length > 0) {
        this.createBackup(filePath, code);
        fs.writeFileSync(filePath, output.code, 'utf-8');
      }

      result.success = result.changes.length > 0;
    } catch (error) {
      result.errors.push(`Transform failed: ${error instanceof Error ? error.message : String(error)}`);
    }

    return result;
  }

  private createBackup(filePath: string, code: string): void {
    if (!fs.existsSync(this.config.backupDir)) {
      fs.mkdirSync(this.config.backupDir, { recursive: true });
    }

    const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
    const basename = path.basename(filePath);
    const backupPath = path.join(this.config.backupDir, `${timestamp}_${basename}.backup`);

    fs.writeFileSync(backupPath, code, 'utf-8');
    this.backupManifest.set(filePath, backupPath);
  }

  private async rollbackFile(filePath: string): Promise<void> {
    const backupPath = this.backupManifest.get(filePath);
    if (backupPath && fs.existsSync(backupPath)) {
      const backupContent = fs.readFileSync(backupPath, 'utf-8');
      fs.writeFileSync(filePath, backupContent, 'utf-8');
      fs.unlinkSync(backupPath);
      this.backupManifest.delete(filePath);
    }
  }

  // ========================================
  // Utility Methods
  // ========================================

  private send(ws: WebSocket, message: MigrationMessage): void {
    if (ws.readyState === WebSocket.OPEN) {
      ws.send(JSON.stringify(message));
    }
  }

  private sendError(ws: WebSocket, code: string, message: string, details?: unknown): void {
    const errorMsg: MigrationMessage = {
      type: 'error',
      timestamp: Date.now(),
      id: '',
      code,
      message,
      details
    };
    this.send(ws, errorMsg);
  }

  // ========================================
  // Server Lifecycle
  // ========================================

  start(): Promise<void> {
    return new Promise((resolve) => {
      this.server.listen(this.config.port, this.config.host, () => {
        console.log(`Migration server running at http://${this.config.host}:${this.config.port}`);
        console.log(`WebSocket endpoint: ws://${this.config.host}:${this.config.port}`);
        resolve();
      });
    });
  }

  stop(): Promise<void> {
    return new Promise((resolve, reject) => {
      this.wss.close((err) => {
        if (err) reject(err);
        else resolve();
      });
      this.server.close();
    });
  }
}

// ========================================
// CLI Entry Point
// ========================================

async function main() {
  const args = process.argv.slice(2);
  let port = defaultConfig.port;

  for (let i = 0; i < args.length; i++) {
    if (args[i] === '--port' || args[i] === '-p') {
      port = parseInt(args[++i], 10);
    }
  }

  const server = new MigrationServer({ port });
  await server.start();

  // Handle graceful shutdown
  process.on('SIGINT', async () => {
    console.log('\nShutting down...');
    await server.stop();
    process.exit(0);
  });

  process.on('SIGTERM', async () => {
    await server.stop();
    process.exit(0);
  });
}

main().catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});

export { MigrationServer };
