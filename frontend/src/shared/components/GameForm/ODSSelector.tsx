// @ts-nocheck - TypeScript strict mode temporarily disabled for gradual migration
/**
 * ODSSelector Component
 *
 * 卡片式ODS数据库选择器 - GameForm的优秀UX特性
 * 支持点击选择,带图标和描述
 */

import React from 'react';
import styles from './ODSSelector.module.css';

export type ODSType = 'domestic' | 'overseas';

interface ODSSelectorProps {
  /** 当前选中的ODS类型 */
  value?: ODSType;
  /** 值变化回调 */
  onChange: (value: ODSType) => void;
  /** 是否禁用 */
  disabled?: boolean;
  /** 错误信息 */
  error?: string | null;
}

export const ODSSelector = ({
  value = 'domestic',
  onChange,
  disabled = false,
  error = null
}: ODSSelectorProps): React.JSX.Element => {
  const isDomestic = value === 'domestic';

  return (
    <div className={styles.odsOptions}>
      {error && (
        <div className={styles.errorMessage}>{error}</div>
      )}
      {/* Domestic Option */}
      <div
        className={`${styles.optionCard} ${isDomestic ? styles.selected : ''}`}
        onClick={() => !disabled && onChange('domestic')}
        data-testid="ods-type-domestic"
      >
        <div className={styles.optionCardContent}>
          <input
            className={styles.formCheckInput}
            type="radio"
            id="ods_type_domestic"
            name="ods_type"
            checked={isDomestic}
            onChange={() => onChange('domestic')}
            disabled={disabled}
          />
          <div className={styles.optionContent}>
            <div className={styles.optionCardTitle}>
              <i className={`bi bi-house ${styles.optionCardIcon} ${styles.iconBlue}`}></i>
              国内 (ieu_ods)
            </div>
            <p className={styles.optionCardDescription}>
              用于国内服务器，使用 ieu_ods 数据库
            </p>
          </div>
        </div>
      </div>

      {/* Overseas Option */}
      <div
        className={`${styles.optionCard} ${!isDomestic ? styles.selectedGreen : ''}`}
        onClick={() => !disabled && onChange('overseas')}
        data-testid="ods-type-overseas"
      >
        <div className={styles.optionCardContent}>
          <input
            className={styles.formCheckInput}
            type="radio"
            id="ods_type_overseas"
            name="ods_type"
            checked={!isDomestic}
            onChange={() => onChange('overseas')}
            disabled={disabled}
          />
          <div className={styles.optionContent}>
            <div className={styles.optionCardTitle}>
              <i className={`bi bi-globe ${styles.optionCardIcon} ${styles.iconGreen}`}></i>
              海外 (hdy_data_sg)
            </div>
            <p className={styles.optionCardDescription}>
              用于海外服务器，使用 hdy_data_sg 数据库
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default React.memo(ODSSelector);
