import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

const sourceDir = path.join(__dirname, '../node_modules/bootstrap-italia/dist');
const targetDir = path.join(__dirname, '../public/bootstrap-italia');

// Crea la directory di destinazione se non esiste
if (!fs.existsSync(targetDir)) {
  fs.mkdirSync(targetDir, { recursive: true });
}

// Copia i file necessari
const copyRecursive = (src, dest) => {
  if (fs.existsSync(src)) {
    if (fs.lstatSync(src).isDirectory()) {
      if (!fs.existsSync(dest)) {
        fs.mkdirSync(dest);
      }
      fs.readdirSync(src).forEach(item => {
        copyRecursive(path.join(src, item), path.join(dest, item));
      });
    } else {
      fs.copyFileSync(src, dest);
    }
  }
};

copyRecursive(sourceDir, targetDir);
console.log('Bootstrap Italia assets copiati con successo!');