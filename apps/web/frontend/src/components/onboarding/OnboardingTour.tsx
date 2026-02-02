import { useCallback, useEffect, useMemo, useState } from 'react';
import styles from './OnboardingTour.module.css';
import { onboardingMessages, type OnboardingMessageKey } from './onboardingMessages';

const ONBOARDING_STORAGE_KEY = 'ppm-home-onboarding-complete';

const steps: { key: OnboardingMessageKey; selector: string }[] = [
  { key: 'welcome', selector: '[data-tour="home-header"]' },
  { key: 'canvas', selector: '[data-tour="home-canvas"]' },
  { key: 'quickAccess', selector: '[data-tour="home-quick-access"]' },
  { key: 'configuration', selector: '[data-tour="home-configuration"]' },
];

const getTargetElement = (selector: string) =>
  typeof document === 'undefined' ? null : (document.querySelector(selector) as HTMLElement | null);

export function OnboardingTour() {
  const [activeStep, setActiveStep] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const [targetRect, setTargetRect] = useState<DOMRect | null>(null);

  const step = steps[activeStep];

  const updateTarget = useCallback(() => {
    const element = getTargetElement(step.selector);
    if (!element) {
      setTargetRect(null);
      return;
    }
    element.scrollIntoView({ behavior: 'smooth', block: 'center' });
    setTargetRect(element.getBoundingClientRect());
  }, [step.selector]);

  useEffect(() => {
    const completed = localStorage.getItem(ONBOARDING_STORAGE_KEY);
    if (completed !== 'true') {
      setIsVisible(true);
    }
  }, []);

  useEffect(() => {
    if (!isVisible) return;
    updateTarget();
  }, [isVisible, updateTarget, activeStep]);

  useEffect(() => {
    if (!isVisible) return;
    const handleResize = () => updateTarget();
    window.addEventListener('resize', handleResize);
    window.addEventListener('scroll', handleResize, true);
    return () => {
      window.removeEventListener('resize', handleResize);
      window.removeEventListener('scroll', handleResize, true);
    };
  }, [isVisible, updateTarget]);

  useEffect(() => {
    if (!isVisible) return;
    const element = getTargetElement(step.selector);
    if (!element) return;
    element.classList.add('onboarding-highlight');
    return () => {
      element.classList.remove('onboarding-highlight');
    };
  }, [isVisible, step.selector]);

  const completeTour = useCallback(() => {
    localStorage.setItem(ONBOARDING_STORAGE_KEY, 'true');
    setIsVisible(false);
  }, []);

  const goNext = useCallback(() => {
    if (activeStep === steps.length - 1) {
      completeTour();
      return;
    }
    setActiveStep((prev) => Math.min(prev + 1, steps.length - 1));
  }, [activeStep, completeTour]);

  const goBack = useCallback(() => {
    setActiveStep((prev) => Math.max(prev - 1, 0));
  }, []);

  const tooltipStyle = useMemo(() => {
    if (!targetRect) return undefined;
    const top = targetRect.bottom + window.scrollY + 12;
    const left = Math.min(targetRect.left + window.scrollX, window.innerWidth - 360);
    return { top, left };
  }, [targetRect]);

  if (!isVisible || !step) return null;

  return (
    <div className={styles.overlay} role="dialog" aria-modal="true">
      <div className={styles.backdrop} />
      <div className={styles.tooltip} style={tooltipStyle}>
        <p className={styles.stepCount}>
          {activeStep + 1} / {steps.length}
        </p>
        <h2 className={styles.title}>{onboardingMessages.title[step.key]}</h2>
        <p className={styles.body}>{onboardingMessages.body[step.key]}</p>
        <div className={styles.actions}>
          <button className={styles.secondaryButton} onClick={completeTour}>
            {onboardingMessages.actions.skip}
          </button>
          <div className={styles.navigationButtons}>
            <button
              className={styles.secondaryButton}
              onClick={goBack}
              disabled={activeStep === 0}
            >
              {onboardingMessages.actions.back}
            </button>
            <button className={styles.primaryButton} onClick={goNext}>
              {activeStep === steps.length - 1
                ? onboardingMessages.actions.finish
                : onboardingMessages.actions.next}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
