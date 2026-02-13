import { Event, Parameter, Field, FieldConfig } from '@shared/types/fieldBuilder';
import { generateHQL } from '@shared/utils/fieldBuilder';

const API_BASE = '/api';

// 获取事件列表
export async function fetchEvents(gameGid: number): Promise<Event[]> {
  const response = await fetch(`${API_BASE}/events?game_gid=${gameGid}`);
  const result = await response.json();
  return result.data.events;
}

// 获取事件参数
export async function fetchEventParameters(eventId: number): Promise<Parameter[]> {
  const response = await fetch(`${API_BASE}/events/${eventId}/parameters`);
  const result = await response.json();
  return result.data;  // API返回的data直接是参数数组，不是data.parameters
}

// 保存配置
export async function saveFieldConfig(config: FieldConfig): Promise<{ id: number }> {
  const response = await fetch(`${API_BASE}/field-builder/configs`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(config)
  });
  const result = await response.json();
  return result.data;
}

// 加载配置
export async function loadFieldConfig(configId: number): Promise<FieldConfig> {
  const response = await fetch(`${API_BASE}/field-builder/configs/${configId}`);
  const result = await response.json();
  return result.data;
}

// 预览HQL
export async function previewHQL(fields: Field[], eventId: number, mode: 'view' | 'procedure'): Promise<string> {
  // TODO: 调用后端API生成HQL
  return generateHQL(fields, `event_${eventId}`, mode);
}
