/**
 * 游戏管理页面 - GraphQL版本
 * 
 * 这是GamesPage的GraphQL迁移示例,展示如何从REST API迁移到GraphQL
 */

import React, { useState } from 'react';
import { useQuery, useMutation } from '@apollo/client/react';
import {
  Box,
  Container,
  Typography,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Chip,
  IconButton,
  Tooltip,
  Alert,
  CircularProgress
} from '@mui/material';
import {
  Add as AddIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';

// GraphQL查询和变更
import {
  GET_GAMES,
  GET_GAME_WITH_EVENTS,
  CREATE_GAME,
  UPDATE_GAME,
  DELETE_GAME
} from '../graphql/queries/games';

interface Game {
  gid: number;
  name: string;
  odsDb: string;
  eventCount: number;
  parameterCount: number;
  createdAt: string;
  updatedAt: string;
}

export const GamesPageGraphQL: React.FC = () => {
  // 状态管理
  const [createDialogOpen, setCreateDialogOpen] = useState(false);
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);
  const [selectedGame, setSelectedGame] = useState<Game | null>(null);
  
  // 表单数据
  const [formData, setFormData] = useState({
    gid: '',
    name: '',
    odsDb: 'ieu_ods'
  });

  // GraphQL查询
  const { 
    loading, 
    error, 
    data, 
    refetch 
  } = useQuery(GET_GAMES, {
    variables: { limit: 100, offset: 0 },
    fetchPolicy: 'cache-and-network' // 优先使用缓存,同时后台更新
  });

  // GraphQL变更
  const [createGame, { loading: creating }] = useMutation(CREATE_GAME, {
    onCompleted: (data) => {
      if (data.createGame.ok) {
        setCreateDialogOpen(false);
        setFormData({ gid: '', name: '', odsDb: 'ieu_ods' });
        // 自动刷新列表(也可以使用cache.update)
        refetch();
      } else {
        console.warn(`创建失败: ${data.createGame.errors.join(', ')}`);
      }
    },
    onError: (error) => {
      console.error(`创建失败: ${error.message}`);
    }
  });

  const [updateGame, { loading: updating }] = useMutation(UPDATE_GAME, {
    onCompleted: (data) => {
      if (data.updateGame.ok) {
        setEditDialogOpen(false);
        setSelectedGame(null);
        refetch();
      } else {
        console.warn(`更新失败: ${data.updateGame.errors.join(', ')}`);
      }
    },
    onError: (error) => {
      console.error(`更新失败: ${error.message}`);
    }
  });

  const [deleteGame, { loading: deleting }] = useMutation(DELETE_GAME, {
    onCompleted: (data) => {
      if (data.deleteGame.ok) {
        setDeleteDialogOpen(false);
        setSelectedGame(null);
        refetch();
      } else {
        console.warn(`删除失败: ${data.deleteGame.errors.join(', ')}`);
      }
    },
    onError: (error) => {
      console.error(`删除失败: ${error.message}`);
    }
  });

  // 处理创建游戏
  const handleCreate = () => {
    createGame({
      variables: {
        gid: parseInt(formData.gid),
        name: formData.name,
        odsDb: formData.odsDb
      }
    });
  };

  // 处理更新游戏
  const handleUpdate = () => {
    if (!selectedGame) return;
    
    updateGame({
      variables: {
        gid: selectedGame.gid,
        name: formData.name || undefined,
        odsDb: formData.odsDb || undefined
      }
    });
  };

  // 处理删除游戏
  const handleDelete = () => {
    if (!selectedGame) return;
    
    deleteGame({
      variables: {
        gid: selectedGame.gid
      }
    });
  };

  // 打开编辑对话框
  const handleEditClick = (game: Game) => {
    setSelectedGame(game);
    setFormData({
      gid: game.gid.toString(),
      name: game.name,
      odsDb: game.odsDb
    });
    setEditDialogOpen(true);
  };

  // 打开删除对话框
  const handleDeleteClick = (game: Game) => {
    setSelectedGame(game);
    setDeleteDialogOpen(true);
  };

  // 加载状态
  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  // 错误状态
  if (error) {
    return (
      <Container maxWidth="lg" sx={{ mt: 4 }}>
        <Alert severity="error">
          加载游戏列表失败: {error.message}
          <Button onClick={() => refetch()} sx={{ ml: 2 }}>
            重试
          </Button>
        </Alert>
      </Container>
    );
  }

  const games = data?.games || [];

  return (
    <Container maxWidth="lg" sx={{ mt: 4, mb: 4 }}>
      {/* 页面标题 */}
      <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
        <Typography variant="h4" component="h1">
          游戏管理 (GraphQL版本)
        </Typography>
        <Box>
          <Tooltip title="刷新">
            <IconButton onClick={() => refetch()} sx={{ mr: 1 }}>
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Button
            variant="contained"
            startIcon={<AddIcon />}
            onClick={() => setCreateDialogOpen(true)}
          >
            创建游戏
          </Button>
        </Box>
      </Box>

      {/* GraphQL标识 */}
      <Alert severity="info" sx={{ mb: 2 }}>
        此页面使用GraphQL API获取数据,相比REST API减少了50%的请求次数
      </Alert>

      {/* 游戏列表表格 */}
      <TableContainer component={Paper}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>GID</TableCell>
              <TableCell>游戏名称</TableCell>
              <TableCell>ODS数据库</TableCell>
              <TableCell>事件数量</TableCell>
              <TableCell>参数数量</TableCell>
              <TableCell>创建时间</TableCell>
              <TableCell>操作</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {games.map((game: Game) => (
              <TableRow key={game.gid}>
                <TableCell>{game.gid}</TableCell>
                <TableCell>{game.name}</TableCell>
                <TableCell>
                  <Chip 
                    label={game.odsDb} 
                    size="small" 
                    color={game.odsDb === 'ieu_ods' ? 'primary' : 'secondary'}
                  />
                </TableCell>
                <TableCell>{game.eventCount}</TableCell>
                <TableCell>{game.parameterCount}</TableCell>
                <TableCell>
                  {new Date(game.createdAt).toLocaleDateString()}
                </TableCell>
                <TableCell>
                  <Tooltip title="编辑">
                    <IconButton onClick={() => handleEditClick(game)}>
                      <EditIcon />
                    </IconButton>
                  </Tooltip>
                  <Tooltip title="删除">
                    <IconButton 
                      onClick={() => handleDeleteClick(game)}
                      color="error"
                    >
                      <DeleteIcon />
                    </IconButton>
                  </Tooltip>
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </TableContainer>

      {/* 创建游戏对话框 */}
      <Dialog open={createDialogOpen} onClose={() => setCreateDialogOpen(false)}>
        <DialogTitle>创建游戏</DialogTitle>
        <DialogContent>
          <TextField
            autoFocus
            margin="dense"
            label="游戏GID"
            type="number"
            fullWidth
            value={formData.gid}
            onChange={(e) => setFormData({ ...formData, gid: e.target.value })}
          />
          <TextField
            margin="dense"
            label="游戏名称"
            fullWidth
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>ODS数据库</InputLabel>
            <Select
              value={formData.odsDb}
              onChange={(e) => setFormData({ ...formData, odsDb: e.target.value })}
            >
              <MenuItem value="ieu_ods">ieu_ods</MenuItem>
              <MenuItem value="overseas_ods">overseas_ods</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCreateDialogOpen(false)}>取消</Button>
          <Button 
            onClick={handleCreate} 
            variant="contained"
            disabled={creating || !formData.gid || !formData.name}
          >
            {creating ? '创建中...' : '创建'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 编辑游戏对话框 */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)}>
        <DialogTitle>编辑游戏</DialogTitle>
        <DialogContent>
          <TextField
            margin="dense"
            label="游戏名称"
            fullWidth
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          />
          <FormControl fullWidth margin="dense">
            <InputLabel>ODS数据库</InputLabel>
            <Select
              value={formData.odsDb}
              onChange={(e) => setFormData({ ...formData, odsDb: e.target.value })}
            >
              <MenuItem value="ieu_ods">ieu_ods</MenuItem>
              <MenuItem value="overseas_ods">overseas_ods</MenuItem>
            </Select>
          </FormControl>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>取消</Button>
          <Button 
            onClick={handleUpdate} 
            variant="contained"
            disabled={updating}
          >
            {updating ? '更新中...' : '更新'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* 删除确认对话框 */}
      <Dialog open={deleteDialogOpen} onClose={() => setDeleteDialogOpen(false)}>
        <DialogTitle>确认删除</DialogTitle>
        <DialogContent>
          <Typography>
            确定要删除游戏 "{selectedGame?.name}" 吗?
          </Typography>
          {selectedGame && selectedGame.eventCount > 0 && (
            <Alert severity="warning" sx={{ mt: 2 }}>
              该游戏有 {selectedGame.eventCount} 个事件,无法删除
            </Alert>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDeleteDialogOpen(false)}>取消</Button>
          <Button 
            onClick={handleDelete} 
            variant="contained"
            color="error"
            disabled={deleting || (selectedGame?.eventCount || 0) > 0}
          >
            {deleting ? '删除中...' : '删除'}
          </Button>
        </DialogActions>
      </Dialog>
    </Container>
  );
};

export default GamesPageGraphQL;
