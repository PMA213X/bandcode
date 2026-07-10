import { readFileSync, existsSync } from 'fs';
import { resolve } from 'path';

const REPORT_PATH = resolve(import.meta.dirname, 'loop-report.md');

let passed = 0;
let failed = 0;

function assert(condition, message) {
  if (condition) {
    console.log(`  PASS: ${message}`);
    passed++;
  } else {
    console.error(`  FAIL: ${message}`);
    failed++;
  }
}

console.log('--- Loop Report Validation ---\n');

// Test 1: Report file exists
console.log('[Test 1] Report file exists');
const exists = existsSync(REPORT_PATH);
assert(exists, 'loop-report.md exists at docs/compose/loop-report.md');

if (!exists) {
  console.error(`\n${failed} test(s) failed. File not found: ${REPORT_PATH}`);
  process.exit(1);
}

const content = readFileSync(REPORT_PATH, 'utf-8');

// Test 2: Contains status header
console.log('\n[Test 2] Contains status header');
assert(content.includes('## Coder Agent Loop Report'), 'Report has "## Coder Agent Loop Report" header');

// Test 3: Contains IDLE status
console.log('\n[Test 3] Status is IDLE');
assert(content.includes('Status: IDLE'), 'Status field shows IDLE');

// Test 4: Documents blocking on member F
console.log('\n[Test 4] Documents blocking on member F');
assert(content.includes('blocked on member F') || content.includes('blocked on: member F'), 'Reports blocked on member F');

// Test 5: Lists all 6 blocking files
console.log('\n[Test 5] Lists all 6 blocking files');
const requiredFiles = ['package.json', 'tsconfig.json', 'Layout.tsx', 'Chat.tsx', 'Settings.tsx', 'colors.ts'];
const missingFiles = requiredFiles.filter(f => !content.includes(f));
assert(missingFiles.length === 0, `All 6 blocking files listed (missing: ${missingFiles.join(', ') || 'none'})`);

// Test 6: Reports new tasks count
console.log('\n[Test 6] Reports new tasks count');
assert(/New tasks:\s*\d+/.test(content), 'Contains "New tasks: N" line');

// Test 7: Reports completed count
console.log('\n[Test 7] Reports completed count');
assert(/Completed:\s*\d+/.test(content), 'Contains "Completed: N" line');

// Test 8: Lists processed issues
console.log('\n[Test 8] Lists processed issues');
assert(content.includes('#1'), 'References processed issue #1');

// Test 9: Lists implemented files count
console.log('\n[Test 9] Lists implemented files count');
assert(content.includes('11') || content.includes('Implemented files'), 'Documents implemented files count');

// Test 10: Contains ISO timestamp
console.log('\n[Test 10] Contains timestamp');
assert(/\d{4}-\d{2}-\d{2}/.test(content), 'Contains date in YYYY-MM-DD format');

console.log(`\n--- Results: ${passed} passed, ${failed} failed ---`);
process.exit(failed > 0 ? 1 : 0);
