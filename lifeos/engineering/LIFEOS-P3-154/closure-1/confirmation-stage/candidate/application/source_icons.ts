export const icon = (name:string) => {
    const paths:any = {
      today: '<path d="M4 11.5 12 4l8 7.5"/><path d="M6.5 10v8h11v-8"/><path d="M10 18v-4h4v4"/>',
      me: '<circle cx="12" cy="8" r="3.2"/><path d="M5.5 20c.8-4 3-6 6.5-6s5.7 2 6.5 6"/>',
      contexts: '<path d="M4.5 6.5h15v11h-15z"/><path d="M4.5 10h15"/><path d="M8 3.8v5.4M16 3.8v5.4"/>',
      memory: '<path d="M5.2 5.7A3.7 3.7 0 0 1 8.8 4H19v15H8.8a3.7 3.7 0 0 0-3.6 2.5z"/><path d="M5.2 5.7V21.5"/><path d="M8.5 8h7M8.5 11h7"/>',
      settings: '<circle cx="12" cy="12" r="3"/><path d="M19 12a7.1 7.1 0 0 0-.1-1.2l2-1.5-2-3.4-2.4 1a7.7 7.7 0 0 0-2-1.2L14.2 3h-4.1l-.4 2.6a7.7 7.7 0 0 0-2 1.2l-2.4-1-2 3.4 2 1.5A7.1 7.1 0 0 0 5 12c0 .4 0 .8.1 1.2l-2 1.5 2 3.4 2.4-1a7.7 7.7 0 0 0 2 1.2l.4 2.6h4.1l.4-2.6a7.7 7.7 0 0 0 2-1.2l2.4 1 2-3.4-2-1.5c.1-.4.1-.8.1-1.2z"/>',
      target: '<circle cx="12" cy="12" r="7.5"/><circle cx="12" cy="12" r="3.3"/><path d="m12 2.5 1.2 2.2M21.5 12l-2.2 1.2M12 21.5l-1.2-2.2M2.5 12l2.2-1.2"/>',
      calendar: '<rect x="4.5" y="5.5" width="15" height="14" rx="2"/><path d="M8 3.5v4M16 3.5v4M4.5 10h15"/>',
      sun: '<circle cx="12" cy="12" r="4"/><path d="M12 2v2.4M12 19.6V22M2 12h2.4M19.6 12H22M4.9 4.9l1.7 1.7M17.4 17.4l1.7 1.7M19.1 4.9l-1.7 1.7M6.6 17.4l-1.7 1.7"/>',
      check: '<path d="m5 12.5 4.2 4.2L19.5 6.5"/>',
      pulse: '<path d="M3 12h4l2.2-5 3.5 10 2.1-5H21"/>',
      heart: '<path d="M20 8.8c0 5-8 10.2-8 10.2S4 13.8 4 8.8C4 6.1 6 4.5 8.2 4.5c1.5 0 2.9.8 3.8 2 1-1.2 2.3-2 3.8-2C18 4.5 20 6.1 20 8.8z"/>',
      clock: '<circle cx="12" cy="12" r="8"/><path d="M12 7v5l3.2 2"/>',
      spark: '<path d="m12 2 1.5 6.5L20 10l-6.5 1.5L12 18l-1.5-6.5L4 10l6.5-1.5z"/><path d="m19 17 .5 2 .5-2 2-.5-2-.5-.5-2-.5 2-2 .5z"/>',
      arrow: '<path d="M5 12h13"/><path d="m13 6 6 6-6 6"/>',
      close: '<path d="m6 6 12 12M18 6 6 18"/>',
      plus: '<path d="M12 5v14M5 12h14"/>',
    };
    return `<svg class="rail-icon" aria-hidden="true" viewBox="0 0 24 24">${paths[name] || paths.spark}</svg>`;
  };
