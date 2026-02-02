export const onboardingMessages = {
  title: {
    welcome: 'Welcome to your PPM workspace',
    canvas: 'Open Canvas quickly',
    quickAccess: 'Jump to work areas',
    configuration: 'Configure your workspace',
  },
  body: {
    welcome:
      'This quick tour highlights the main areas on your home dashboard so you can get started faster.',
    canvas:
      'Launch example artifacts to explore the multi-tab Canvas experience for charters, WBS, and more.',
    quickAccess:
      'Use quick access cards to jump into portfolios, programs, or projects with one click.',
    configuration:
      'Fine-tune agents, connectors, and workflows to match how your organization runs.',
  },
  actions: {
    next: 'Next',
    back: 'Back',
    finish: 'Finish',
    skip: 'Skip tour',
  },
};

export type OnboardingMessageKey = keyof typeof onboardingMessages.title;
