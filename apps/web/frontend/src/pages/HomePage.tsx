import { useNavigate } from 'react-router-dom';
import { OnboardingTour } from '@/components/onboarding/OnboardingTour';
import styles from './HomePage.module.css';

const DEMO_PROJECTS = [
  { id: 'demo-predictive', label: 'Demo Predictive project' },
  { id: 'demo-adaptive', label: 'Demo Adaptive project' },
  { id: 'demo-hybrid', label: 'Demo Hybrid project' },
];

export function HomePage() {
  const navigate = useNavigate();

  return (
    <div className={styles.page}>
      <OnboardingTour />
      <section className={styles.entryCard}>
        <h1>Welcome to the PPM Platform</h1>
        <p>
          Start from assistant quick actions, or launch a fresh intake flow.
        </p>
        <button
          type="button"
          className={styles.primaryButton}
          onClick={() => navigate('/intake/new', { state: { resetAt: Date.now() } })}
        >
          Log new intake
        </button>
      </section>
      <section className={styles.entryCard}>
        <h2>Demo Projects</h2>
        <p>Launch seeded demo projects powered by the same backend workspace APIs.</p>
        <div>
          {DEMO_PROJECTS.map((project) => (
            <button
              key={project.id}
              type="button"
              className={styles.primaryButton}
              onClick={() => navigate(`/projects/${project.id}`)}
            >
              {project.label}
            </button>
          ))}
        </div>
      </section>
    </div>
  );
}

export default HomePage;
