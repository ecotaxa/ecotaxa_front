// SEE: https://commons.wikimedia.org/wiki/Creative_Commons_icons

enum licenseType {
  // DO NOT change the order  
  CC_BY_NC_ND = 0,
  CC_BY_NC_SA,
  CC_BY_NC,
  CC_BY_ND,
  CC_BY_SA,
  CC_BY,
  Copyright,
  CC_0,
  None
};

const licenseURLs: Array<string> =
// DO NOT change the order    
[
  /* CC_BY_NC_ND */ "https://upload.wikimedia.org/wikipedia/commons/f/f1/Cc-by-nc-nd_icon.svg",
  /* CC-BY-NC-SA */ "https://upload.wikimedia.org/wikipedia/commons/1/12/Cc-by-nc-sa_icon.svg",
  /* CC_BY_NC    */ "https://upload.wikimedia.org/wikipedia/commons/9/99/Cc-by-nc_icon.svg",
  /* CC_BY_ND    */ "https://upload.wikimedia.org/wikipedia/commons/1/16/Cc-by-nd_icon.svg",
  /* CC_BY_SA    */ "https://upload.wikimedia.org/wikipedia/commons/0/08/Cc-by-sa_%281%29.svg",
  /* CC_BY       */ "https://upload.wikimedia.org/wikipedia/commons/1/16/CC-BY_icon.svg",
  /* Copyright   */ "https://upload.wikimedia.org/wikipedia/commons/b/bc/Somerights2.png",
  /* CC_0        */ "https://upload.wikimedia.org/wikipedia/commons/6/69/CC0_button.svg",
  /* None        */ "https://upload.wikimedia.org/wikipedia/commons/8/84/Public_Domain_Mark_button.svg"
];

export function computeLicense(projLicense: string): string {
  // DO NOT change the order  
  // J'ai fait un truc un peu "blindé" qui fait abstraction des espaces et/ou tirets et version (4.0 par exemple) car ça varie pas mal.
  // Important : 9 cases, compute from more complex to simplest one
  // CC-BY-NC-ND
  if (
    projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("BY") !== -1 &&
    projLicense.indexOf("NC") !== -1 &&
    projLicense.indexOf("ND") !== -1
  )
    return licenseURLs[licenseType.CC_BY_NC_ND];
  // CC-BY-NC-SA
  if (
    projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("BY") !== -1 &&
    projLicense.indexOf("NC") !== -1 &&
    projLicense.indexOf("SA") !== -1
  )
    return licenseURLs[licenseType.CC_BY_NC_SA];
  // CC-BY-NC
  if (
    projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("BY") !== -1 &&
    projLicense.indexOf("NC") !== -1
  )
    return licenseURLs[licenseType.CC_BY_NC];
  // CC-BY-ND
  if (
    projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("BY") !== -1 &&
    projLicense.indexOf("ND") !== -1
  )
    return licenseURLs[licenseType.CC_BY_ND];
  // CC-BY-SA
  if (
    projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("BY") !== -1 &&
    projLicense.indexOf("SA") !== -1
  )
    return licenseURLs[licenseType.CC_BY_SA];
  // CC-BY
  if (
    projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("BY") !== -1
  )
    return licenseURLs[licenseType.CC_BY];
  // Copyright
  if (projLicense.indexOf("Copyright") !== -1) {
    return licenseURLs[licenseType.Copyright];
  }
  // CC_0
  if (projLicense.indexOf("CC") !== -1 &&
    projLicense.indexOf("0") !== -1) {
    return licenseURLs[licenseType.CC_0];
  }
  // Default if not specified
  return licenseURLs[licenseType.None];
}
