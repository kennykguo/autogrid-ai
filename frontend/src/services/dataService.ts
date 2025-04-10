// Temporary data for development
const temporaryData = {
  gridStatus: {
    connected: true,
    lastUpdate: new Date().toISOString()
  },
  currentPower: {
    value: 2.4,
    unit: 'MW',
    trend: '+12%'
  },
  solarGeneration: {
    value: 1.2,
    unit: 'MW',
    trend: '+8%'
  },
  batteryLevel: {
    value: 78,
    unit: '%',
    trend: '-5%'
  },
  gridImport: {
    value: 0.8,
    unit: 'MW',
    trend: '-15%'
  },
  energySources: {
    solar: [0, 0.2, 1.5, 2.5, 2.0, 0.5, 0, 0],
    wind: [0.5, 0.8, 1.0, 0.8, 0.5, 0.6, 0.7, 0.6],
    grid: [1.2, 1.0, 0.8, 0.5, 0.2, 0.3, 0.8, 1.0],
    battery: [0.3, 0.2, 0.1, 0, -0.3, -0.2, 0, 0.1],
    times: ['00:00', '03:00', '06:00', '09:00', '12:00', '15:00', '18:00', '21:00']
  }
};

// API endpoints (to be implemented)
const API_ENDPOINTS = {
  GRID_STATUS: '/api/grid-status',
  CURRENT_POWER: '/api/current-power',
  SOLAR_GENERATION: '/api/solar-generation',
  BATTERY_LEVEL: '/api/battery-level',
  GRID_IMPORT: '/api/grid-import',
  ENERGY_SOURCES: '/api/energy-sources'
};

// Data fetching functions
export const fetchGridStatus = async () => {
  // TODO: Implement actual API call
  // const response = await fetch(API_ENDPOINTS.GRID_STATUS);
  // return await response.json();
  return temporaryData.gridStatus;
};

export const fetchCurrentPower = async () => {
  // TODO: Implement actual API call
  return temporaryData.currentPower;
};

export const fetchSolarGeneration = async () => {
  // TODO: Implement actual API call
  return temporaryData.solarGeneration;
};

export const fetchBatteryLevel = async () => {
  // TODO: Implement actual API call
  return temporaryData.batteryLevel;
};

export const fetchGridImport = async () => {
  // TODO: Implement actual API call
  return temporaryData.gridImport;
};

export const fetchEnergySources = async () => {
  // TODO: Implement actual API call
  return temporaryData.energySources;
}; 