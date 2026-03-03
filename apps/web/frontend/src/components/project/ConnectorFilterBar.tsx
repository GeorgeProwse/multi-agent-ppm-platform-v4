/**
 * ConnectorFilterBar - Search, category, status, and certification filter controls.
 */

import { CATEGORY_INFO, type ConnectorCategory, type CertificationStatus, type Connector } from '@/store/connectors';
import { Icon } from '@/components/icon/Icon';
import styles from '../connectors/ConnectorGallery.module.css';
import {
  STATUS_OPTIONS,
  CERTIFICATION_OPTIONS,
  type ConnectorFilterBarProps,
} from './projectConnectorTypes';

export function ConnectorFilterBar({
  filter,
  setFilter,
  setCertificationFilter,
  resetFilter,
}: ConnectorFilterBarProps) {
  return (
    <div className={styles.filters}>
      <div className={styles.searchBox}>
        <input
          type="text"
          className={styles.searchInput}
          placeholder="Search connectors..."
          value={filter.search}
          onChange={(e) => setFilter({ search: e.target.value })}
        />
        {filter.search && (
          <button
            className={styles.clearSearch}
            onClick={() => setFilter({ search: '' })}
            title="Clear search"
            aria-label="Clear search"
          >
            <Icon semantic="actions.cancelDismiss" label="Clear search" size="sm" />
          </button>
        )}
      </div>

      <select
        className={styles.categorySelect}
        value={filter.category}
        onChange={(e) => setFilter({ category: e.target.value as ConnectorCategory | 'all' })}
      >
        <option value="all">All Categories</option>
        {Object.values(CATEGORY_INFO).map((cat) => (
          <option key={cat.value} value={cat.value}>
            {cat.label}
          </option>
        ))}
      </select>

      <select
        className={styles.statusSelect}
        value={filter.statusFilter}
        onChange={(e) =>
          setFilter({
            statusFilter: e.target.value as Connector['status'] | 'all',
          })
        }
      >
        {STATUS_OPTIONS.map((status) => (
          <option key={status.value} value={status.value}>
            {status.label}
          </option>
        ))}
      </select>

      <select
        className={styles.statusSelect}
        value={filter.certificationFilter}
        onChange={(e) =>
          setCertificationFilter(e.target.value as CertificationStatus | 'all')
        }
      >
        {CERTIFICATION_OPTIONS.map((status) => (
          <option key={status.value} value={status.value}>
            {status.label}
          </option>
        ))}
      </select>

      <label className={styles.enabledFilter}>
        <input
          type="checkbox"
          checked={filter.enabledOnly}
          onChange={(e) => setFilter({ enabledOnly: e.target.checked })}
        />
        <span>Enabled only</span>
      </label>

      <button className={styles.resetButton} onClick={resetFilter}>
        Reset Filters
      </button>
    </div>
  );
}
