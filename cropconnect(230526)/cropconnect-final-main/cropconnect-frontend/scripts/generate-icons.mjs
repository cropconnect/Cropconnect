import path from "node:path";
import { fileURLToPath } from "node:url";
import sharp from "sharp";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const publicDir = path.resolve(__dirname, "../public");
const sourceIcon = path.join(publicDir, "icon.svg");

const targets = [
  ["icon-192.png", 192],
  ["icon-512.png", 512],
  ["apple-touch-icon.png", 180],
];

await Promise.all(
  targets.map(([filename, size]) =>
    sharp(sourceIcon)
      .resize(size, size)
      .png()
      .toFile(path.join(publicDir, filename)),
  ),
);

console.log("Generated PWA icons from public/icon.svg");
