/**
 * ZIndexManager - 层级管理器
 *
 * 动态管理多个弹窗的z-index层级
 */

/**
 * 弹窗类型枚举
 */
export enum PopupType {
  MODAL = 'modal',
  DRAWER = 'drawer',
  DROPDOWN = 'dropdown',
}

/**
 * 层级范围定义
 */
const Z_RANGES = {
  [PopupType.DROPDOWN]: 1050,
  [PopupType.DRAWER]: 1100,
  [PopupType.MODAL]: 1200,
} as const;

const Z_INCREMENT = 10; // 每增加一个同类型弹窗，层级+10

/**
 * ZIndexManager类
 *
 * 负责分配和管理弹窗的z-index层级
 */
export class ZIndexManager {
  private baseLayers: Record<PopupType, number>;
  private counters: Record<PopupType, number>;

  constructor() {
    this.baseLayers = { ...Z_RANGES };
    this.counters = {
      [PopupType.MODAL]: 0,
      [PopupType.DRAWER]: 0,
      [PopupType.DROPDOWN]: 0,
    };
  }

  /**
   * 获取下一个z-index值
   *
   * @param type - 弹窗类型
   * @returns z-index值
   */
  getNext(type: PopupType): number {
    this.counters[type]++;
    const increment = this.counters[type] * Z_INCREMENT;
    return this.baseLayers[type] + increment - Z_INCREMENT;
  }

  /**
   * 释放一个层级计数（弹窗关闭时调用）
   *
   * @param type - 弹窗类型
   */
  release(type: PopupType): void {
    this.counters[type] = Math.max(0, this.counters[type] - 1);
  }

  /**
   * 获取当前最顶层的弹窗类型
   *
   * @returns 最顶层的弹窗类型，如果没有弹窗则返回null
   */
  getTopmostType(): PopupType | null {
    const allZValues: Array<{ type: PopupType; z: number }> = [];

    Object.entries(this.counters).forEach(([type, count]) => {
      if (count > 0) {
        const popupType = type as PopupType;
        const z = this.baseLayers[popupType] + count * Z_INCREMENT - Z_INCREMENT;
        allZValues.push({ type: popupType, z });
      }
    });

    if (allZValues.length === 0) return null;

    // 返回z-index最大的类型
    allZValues.sort((a, b) => b.z - a.z);
    return allZValues[0].type;
  }
}

export default ZIndexManager;
