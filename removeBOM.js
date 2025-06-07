const fs = require('fs');
const path = require('path');

const folder = './3ds';

function removeBom(filePath) {
    let data = fs.readFileSync(filePath);
    if (data[0] === 0xef && data[1] === 0xbb && data[2] === 0xbf) {
        data = data.slice(3);
        fs.writeFileSync(filePath, data);
        console.log(`Removed BOM from: ${filePath}`);
    }
}

function walk(dir) {
    fs.readdirSync(dir).forEach(file => {
        const fullPath = path.join(dir, file);
        const stat = fs.statSync(fullPath);
        if (stat.isDirectory()) {
            walk(fullPath);
        } else if (fullPath.endsWith('.txt')) {
            removeBom(fullPath);
        }
    });
}

walk(folder);
