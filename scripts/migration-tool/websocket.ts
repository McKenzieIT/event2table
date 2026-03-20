/**
 * WebSocket Communication Protocol for Migration Tool
 * 
 * Defines message types and communication protocol between
 * the migration server and web client.
 */

// ========================================
// Message Types
// ========================================

export interface BaseMessage {
  type: string;
  timestamp: number;
  id: string;
}

export interface FileListRequest extends BaseMessage {
  type: 'file:list:request';
  directory: string;
  pattern?: string;
}

export interface FileListResponse extends BaseMessage {
  type: 'file:list:response';
  files: FileInfo[];
}

export interface FileInfo {
  path: string;
  name: string;
  extension: string;
  size: number;
  lastModified: number;
  hasMigration: boolean;
  migrationType?: string;
}

export interface TransformRequest extends BaseMessage {
  type: 'transform:request';
  filePath: string;
  rules: string[];
  preview: boolean;
}

export interface TransformResponse extends BaseMessage {
  type: 'transform:response';
  filePath: string;
  success: boolean;
  changes: ChangeInfo[];
  warnings: string[];
  errors: string[];
  originalCode: string;
  transformedCode: string;
}

export interface ChangeInfo {
  type: 'import' | 'component' | 'prop' | 'other';
  description: string;
  line?: number;
  column?: number;
  before?: string;
  after?: string;
}

export interface BatchTransformRequest extends BaseMessage {
  type: 'batch:request';
  directory: string;
  rules: string[];
  dryRun: boolean;
}

export interface BatchProgressMessage extends BaseMessage {
  type: 'batch:progress';
  totalFiles: number;
  processedFiles: number;
  currentFile: string;
  status: 'processing' | 'completed' | 'error';
  changes: number;
}

export interface BatchCompleteMessage extends BaseMessage {
  type: 'batch:complete';
  totalFiles: number;
  successfulFiles: number;
  failedFiles: number;
  totalChanges: number;
  duration: number;
  results: TransformResult[];
}

export interface TransformResult {
  filePath: string;
  success: boolean;
  changes: number;
  warnings: number;
  errors: number;
}

export interface RollbackRequest extends BaseMessage {
  type: 'rollback:request';
  filePath?: string;
}

export interface RollbackResponse extends BaseMessage {
  type: 'rollback:response';
  success: boolean;
  rolledBackFiles: string[];
}

export interface RuleListRequest extends BaseMessage {
  type: 'rule:list:request';
}

export interface RuleListResponse extends BaseMessage {
  type: 'rule:list:response';
  rules: RuleInfo[];
}

export interface RuleInfo {
  id: string;
  name: string;
  description: string;
  componentPattern: string;
  enabled: boolean;
}

export interface Error extends BaseMessage {
  type: 'error';
  code: string;
  message: string;
  details?: unknown;
}

export type MigrationMessage =
  | FileListRequest
  | FileListResponse
  | TransformRequest
  | TransformResponse
  | BatchTransformRequest
  | BatchProgressMessage
  | BatchCompleteMessage
  | RollbackRequest
  | RollbackResponse
  | RuleListRequest
  | RuleListResponse
  | Error;

// ========================================
// Message Factory
// ========================================

export class MessageFactory {
  private static generateId(): string {
    return `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  static createFileListRequest(directory: string, pattern?: string): FileListRequest {
    return {
      type: 'file:list:request',
      timestamp: Date.now(),
      id: this.generateId(),
      directory,
      pattern
    };
  }

  static createTransformRequest(
    filePath: string,
    rules: string[],
    preview: boolean = true
  ): TransformRequest {
    return {
      type: 'transform:request',
      timestamp: Date.now(),
      id: this.generateId(),
      filePath,
      rules,
      preview
    };
  }

  static createBatchRequest(
    directory: string,
    rules: string[],
    dryRun: boolean = true
  ): BatchTransformRequest {
    return {
      type: 'batch:request',
      timestamp: Date.now(),
      id: this.generateId(),
      directory,
      rules,
      dryRun
    };
  }

  static createRollbackRequest(filePath?: string): RollbackRequest {
    return {
      type: 'rollback:request',
      timestamp: Date.now(),
      id: this.generateId(),
      filePath
    };
  }

  static createRuleListRequest(): RuleListRequest {
    return {
      type: 'rule:list:request',
      timestamp: Date.now(),
      id: this.generateId()
    };
  }
}

// ========================================
// WebSocket Client Wrapper
// ========================================

export class MigrationWebSocketClient {
  private ws: WebSocket | null = null;
  private messageHandlers: Map<string, (message: MigrationMessage) => void> = new Map();
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;

  constructor(private url: string) {}

  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('WebSocket connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onclose = () => {
          console.log('WebSocket disconnected');
          this.handleReconnect();
        };

        this.ws.onerror = (error) => {
          console.error('WebSocket error:', error);
          reject(error);
        };

        this.ws.onmessage = (event) => {
          try {
            const message: MigrationMessage = JSON.parse(event.data);
            this.handleMessage(message);
          } catch (error) {
            console.error('Failed to parse message:', error);
          }
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      const delay = Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000);
      console.log(`Reconnecting in ${delay}ms (attempt ${this.reconnectAttempts})`);
      setTimeout(() => this.connect(), delay);
    }
  }

  private handleMessage(message: MigrationMessage): void {
    const handler = this.messageHandlers.get(message.type);
    if (handler) {
      handler(message);
    }

    // Also call generic handlers
    const genericHandler = this.messageHandlers.get('*');
    if (genericHandler) {
      genericHandler(message);
    }
  }

  on(type: string, handler: (message: MigrationMessage) => void): void {
    this.messageHandlers.set(type, handler);
  }

  off(type: string): void {
    this.messageHandlers.delete(type);
  }

  send(message: MigrationMessage): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify(message));
    } else {
      console.error('WebSocket is not connected');
    }
  }

  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }
}
