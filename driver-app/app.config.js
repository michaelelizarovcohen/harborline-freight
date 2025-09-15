// Dynamic Expo config: secrets come from the build environment (EAS secrets),
// never from app.json. See docs/runbooks/mobile-release.md.
const base = require("./app.json");

module.exports = () => {
  const expo = base.expo;
  return {
    ...expo,
    android: {
      ...expo.android,
      config: {
        ...(expo.android.config || {}),
        googleMaps: {
          apiKey: process.env.GOOGLE_MAPS_ANDROID_KEY || "",
        },
      },
    },
    ios: {
      ...expo.ios,
      config: {
        ...(expo.ios.config || {}),
        googleMapsApiKey: process.env.GOOGLE_MAPS_IOS_KEY || "",
      },
    },
    extra: {
      ...expo.extra,
      apiBaseUrl: process.env.HBL_API_BASE_URL || expo.extra.apiBaseUrl,
      releaseChannel: process.env.EAS_BUILD_PROFILE || "development",
    },
  };
};
