import * as readline from 'node:readline/promises';
import { stdin as input, stdout as output } from 'node:process';
import {LoginSession, EAuthTokenPlatformType} from 'steam-session';

const rl = readline.createInterface({ input, output });
const refreshToken = await rl.question('ck: ');

let session = new LoginSession(EAuthTokenPlatformType.SteamClient);
session.refreshToken = refreshToken
await session.refreshAccessToken();

console.log(`\ncookies: steamLoginSecure=${session.steamID}%7C%7C${session.accessToken}`);


// node index.js 