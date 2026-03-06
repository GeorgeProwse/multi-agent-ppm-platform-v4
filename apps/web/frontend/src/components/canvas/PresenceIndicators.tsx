import styles from './PresenceIndicators.module.css';

export interface Participant {
  userId: string;
  name: string;
  color: string;
  joinedAt: number;
}

interface PresenceIndicatorsProps {
  participants: Participant[];
}

function getInitials(name: string): string {
  return name
    .split(' ')
    .map(w => w[0])
    .join('')
    .toUpperCase()
    .slice(0, 2);
}

export function PresenceIndicators({ participants }: PresenceIndicatorsProps) {
  if (participants.length === 0) return null;

  return (
    <div className={styles.container}>
      {participants.map(p => (
        <div
          key={p.userId}
          className={styles.avatar}
          style={{ background: p.color }}
          title={`${p.name} (editing)`}
        >
          {getInitials(p.name)}
          <span className={styles.pulse} />
        </div>
      ))}
      <span className={styles.count}>{participants.length} editing</span>
    </div>
  );
}
