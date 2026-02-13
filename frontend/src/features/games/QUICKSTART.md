# GameManagementModal 快速开始

## 🚀 5分钟快速集成

### 步骤 1: 导入组件

```jsx
import { GameManagementModal } from '@/features/games';
```

### 步骤 2: 添加状态管理

```jsx
const [isModalOpen, setIsModalOpen] = useState(false);
```

### 步骤 3: 渲染组件

```jsx
function MyApp() {
  return (
    <>
      <Button onClick={() => setIsModalOpen(true)}>
        游戏管理
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </>
  );
}
```

## 📝 常见使用场景

### 场景 1: 导航栏集成

```jsx
function Navigation() {
  const [isModalOpen, setIsModalOpen] = useState(false);

  return (
    <nav>
      <Button onClick={() => setIsModalOpen(true)}>
        游戏管理
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
      />
    </nav>
  );
}
```

### 场景 2: 带数据刷新

```jsx
import { useGameStore } from '@/stores/gameStore';

function Dashboard() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const { currentGame, setCurrentGame } = useGameStore();

  const handleClose = () => {
    setIsModalOpen(false);

    // 刷新当前游戏数据
    if (currentGame) {
      fetch(`/api/games/${currentGame.gid}`)
        .then(res => res.json())
        .then(data => {
          if (data.success) setCurrentGame(data.data);
        });
    }
  };

  return (
    <>
      <Button onClick={() => setIsModalOpen(true)}>
        管理游戏
      </Button>

      <GameManagementModal
        isOpen={isModalOpen}
        onClose={handleClose}
      />
    </>
  );
}
```

### 场景 3: 作为设置页面

```jsx
function Settings() {
  const [showGameSettings, setShowGameSettings] = useState(false);

  return (
    <div className="settings">
      <h2>系统设置</h2>

      <section>
        <h3>游戏管理</h3>
        <Button onClick={() => setShowGameSettings(true)}>
          打开游戏管理
        </Button>
      </section>

      <GameManagementModal
        isOpen={showGameSettings}
        onClose={() => setShowGameSettings(false)}
      />
    </div>
  );
}
```

## 🎯 Props 说明

### GameManagementModal

| Prop | 类型 | 默认值 | 必需 | 说明 |
|------|------|--------|------|------|
| isOpen | boolean | false | ✅ | 控制模态框显示/隐藏 |
| onClose | function | - | ✅ | 关闭回调函数 |

## 💡 使用技巧

### 1. 键盘快捷键

```jsx
useEffect(() => {
  const handleKeyDown = (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'g') {
      e.preventDefault();
      setIsModalOpen(true);
    }
  };

  window.addEventListener('keydown', handleKeyDown);
  return () => window.removeEventListener('keydown', handleKeyDown);
}, []);
```

### 2. 自动刷新数据

```jsx
const queryClient = useQueryClient();

const handleClose = () => {
  setIsModalOpen(false);
  queryClient.invalidateQueries(['games']);
};
```

### 3. 保存后回调

```jsx
const handleSave = () => {
  // 自定义保存后逻辑
  console.log('游戏已更新');
};

// 注意: 当前版本不支持 onSave prop
// 请使用 React Query 的 invalidateQueries
```

## ⚠️ 常见问题

### Q: 如何监听游戏变化？

```jsx
// 使用 gameStore
import { useGameStore } from '@/stores/gameStore';

function Component() {
  const { currentGame } = useGameStore();

  useEffect(() => {
    if (currentGame) {
      console.log('当前游戏:', currentGame);
    }
  }, [currentGame]);
}
```

### Q: 如何处理删除错误？

```jsx
// 组件内部已处理错误
// 错误会显示为 Toast 通知
// 无需额外处理
```

### Q: 如何自定义样式？

```jsx
// 修改 GameManagementModal.css
// 或通过 className 覆盖样式

<GameManagementModal
  isOpen={isOpen}
  onClose={handleClose}
  className="custom-modal"
/>
```

## 📚 更多资源

- [完整文档](./README.md) - 详细的组件文档
- [示例集合](./GameManagementModal.example.jsx) - 6个使用示例
- [集成示例](./GameManagementModal.integration.jsx) - 6个集成方案
- [实现总结](./IMPLEMENTATION_SUMMARY.md) - 完整实现说明

## 🔗 相关组件

- [Modal](../../shared/ui/Modal/Modal.jsx) - 基础模态框组件
- [Button](../../shared/ui/Button/Button.jsx) - 按钮组件
- [Input](../../shared/ui/Input/Input.jsx) - 输入框组件
- [Checkbox](../../shared/ui/Checkbox/Checkbox.jsx) - 复选框组件

---

**版本**: 1.0.0
**更新**: 2026-02-13
