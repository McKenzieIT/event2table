/**
 * Input Component Examples
 * 
 * 展示 Input 组件的各种用法
 */

import React, { useState } from 'react';
import { Input } from '@shared/ui';

export function InputBasicExample() {
  return (
    <div className="example-section">
      <h3>基础用法</h3>
      <div className="input-group">
        <Input
          type="text"
          label="用户名"
          placeholder="请输入用户名"
        />
        <Input
          type="email"
          label="邮箱"
          placeholder="请输入邮箱地址"
        />
        <Input
          type="password"
          label="密码"
          placeholder="请输入密码"
        />
      </div>
    </div>
  );
}

export function InputTypesExample() {
  return (
    <div className="example-section">
      <h3>不同类型</h3>
      <div className="input-group">
        <Input type="text" label="文本" placeholder="文本输入" />
        <Input type="number" label="数字" placeholder="数字输入" />
        <Input type="tel" label="电话" placeholder="电话号码" />
        <Input type="url" label="网址" placeholder="https://" />
        <Input type="search" label="搜索" placeholder="搜索内容" />
        <Input type="date" label="日期" />
        <Input type="time" label="时间" />
        <Input type="color" label="颜色" />
      </div>
    </div>
  );
}

export function InputValidationExample() {
  const [values, setValues] = useState({
    username: '',
    email: '',
    password: ''
  });

  const [errors, setErrors] = useState({
    username: '',
    email: '',
    password: ''
  });

  const validateEmail = (email: string) => {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
  };

  const handleChange = (field: string, value: string) => {
    setValues({ ...values, [field]: value });

    // 实时验证
    if (field === 'username') {
      setErrors({
        ...errors,
        username: value.length < 3 ? '用户名至少需要3个字符' : ''
      });
    } else if (field === 'email') {
      setErrors({
        ...errors,
        email: value && !validateEmail(value) ? '请输入有效的邮箱地址' : ''
      });
    } else if (field === 'password') {
      setErrors({
        ...errors,
        password: value.length < 6 ? '密码至少需要6个字符' : ''
      });
    }
  };

  return (
    <div className="example-section">
      <h3>表单验证</h3>
      <div className="input-group">
        <Input
          type="text"
          label="用户名"
          placeholder="至少3个字符"
          value={values.username}
          onChange={(e) => handleChange('username', e.target.value)}
          error={errors.username}
          required
        />
        <Input
          type="email"
          label="邮箱"
          placeholder="example@email.com"
          value={values.email}
          onChange={(e) => handleChange('email', e.target.value)}
          error={errors.email}
          required
        />
        <Input
          type="password"
          label="密码"
          placeholder="至少6个字符"
          value={values.password}
          onChange={(e) => handleChange('password', e.target.value)}
          error={errors.password}
          required
        />
      </div>
    </div>
  );
}

export function InputStatesExample() {
  return (
    <div className="example-section">
      <h3>状态示例</h3>
      <div className="input-group">
        <Input
          type="text"
          label="禁用状态"
          placeholder="无法输入"
          disabled
        />
        <Input
          type="text"
          label="只读状态"
          placeholder="只读内容"
          defaultValue="这是只读内容"
          readOnly
        />
        <Input
          type="text"
          label="错误状态"
          placeholder="输入错误"
          error="输入内容格式不正确"
        />
        <Input
          type="text"
          label="必填字段"
          placeholder="必填"
          required
        />
      </div>
    </div>
  );
}

export function InputHelperExample() {
  return (
    <div className="example-section">
      <h3>辅助文本</h3>
      <div className="input-group">
        <Input
          type="text"
          label="用户名"
          placeholder="请输入用户名"
          helperText="用户名由字母、数字和下划线组成"
        />
        <Input
          type="password"
          label="密码"
          placeholder="请输入密码"
          helperText="密码长度至少8位，包含字母和数字"
        />
        <Input
          type="text"
          label="描述"
          placeholder="请输入描述"
          helperText="最多200个字符"
          maxLength={200}
        />
      </div>
    </div>
  );
}

export function InputWithIconExample() {
  const SearchIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <circle cx="11" cy="11" r="8" />
      <path d="m21 21-4.35-4.35" />
    </svg>
  );

  const UserIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
      <circle cx="12" cy="7" r="4" />
    </svg>
  );

  const LockIcon = () => (
    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
      <rect width="18" height="11" x="3" y="11" rx="2" ry="2" />
      <path d="M7 11V7a5 5 0 0 1 10 0v4" />
    </svg>
  );

  return (
    <div className="example-section">
      <h3>带图标输入框</h3>
      <div className="input-group">
        <Input
          type="text"
          label="搜索"
          placeholder="搜索内容..."
          icon={SearchIcon}
        />
        <Input
          type="text"
          label="用户名"
          placeholder="请输入用户名"
          icon={UserIcon}
        />
        <Input
          type="password"
          label="密码"
          placeholder="请输入密码"
          icon={LockIcon}
        />
      </div>
    </div>
  );
}

export function InputControlledExample() {
  const [value, setValue] = useState('');
  const [count, setCount] = useState(0);

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setValue(e.target.value);
    setCount(e.target.value.length);
  };

  return (
    <div className="example-section">
      <h3>受控组件</h3>
      <div className="input-group">
        <Input
          type="text"
          label="实时字数统计"
          placeholder="输入内容..."
          value={value}
          onChange={handleChange}
          helperText={`已输入 ${count} 个字符`}
        />
        <div className="controlled-display">
          <strong>输入内容：</strong>
          <span>{value || '(空)'}</span>
        </div>
      </div>
    </div>
  );
}

export function InputBestPractices() {
  return (
    <div className="example-section">
      <h3>最佳实践</h3>
      <div className="best-practices">
        <div className="practice-item">
          <h4>1. 始终提供清晰的标签</h4>
          <Input
            type="text"
            label="用户名"
            placeholder="请输入用户名"
          />
        </div>
        <div className="practice-item">
          <h4>2. 使用占位符提供输入提示</h4>
          <Input
            type="email"
            label="邮箱"
            placeholder="example@domain.com"
          />
        </div>
        <div className="practice-item">
          <h4>3. 提供有帮助的辅助文本</h4>
          <Input
            type="password"
            label="密码"
            placeholder="请输入密码"
            helperText="密码长度至少8位"
          />
        </div>
        <div className="practice-item">
          <h4>4. 及时显示验证错误</h4>
          <Input
            type="text"
            label="用户名"
            placeholder="至少3个字符"
            error="用户名太短"
          />
        </div>
        <div className="practice-item">
          <h4>5. 使用图标增强可识别性</h4>
          <Input
            type="text"
            label="搜索"
            placeholder="搜索..."
            icon={() => (
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                <circle cx="11" cy="11" r="8" />
                <path d="m21 21-4.35-4.35" />
              </svg>
            )}
          />
        </div>
      </div>
    </div>
  );
}

export default function InputExamples() {
  return (
    <div className="examples-container">
      <h2>Input 组件示例</h2>
      <InputBasicExample />
      <InputTypesExample />
      <InputValidationExample />
      <InputStatesExample />
      <InputHelperExample />
      <InputWithIconExample />
      <InputControlledExample />
      <InputBestPractices />
    </div>
  );
}
