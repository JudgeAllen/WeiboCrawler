# How to Run Chinese Search Tests

## Quick Start

Run the complete test suite:
```bash
python test_chinese_search.py
```

## Expected Output

You should see:
```
================================================================================
CHINESE SEARCH FUNCTIONALITY TEST SUITE
================================================================================
Database: data/database.db

[... test results ...]

================================================================================
FINAL SUMMARY
================================================================================
  [PASS] Chinese Detection              -> 8 passed, 0 failed
  [PASS] Method Selection               -> 3 passed, 0 failed
  [PASS] Chinese Search                 -> 4 passed, 0 failed
  [PASS] English FTS Search             -> 4 passed, 0 failed
  [PASS] Mixed Search                   -> 2 passed, 0 failed
  [PASS] Special Characters             -> 4 passed, 0 failed

--------------------------------------------------------------------------------
  TOTAL: 25 passed, 0 failed
================================================================================

✓ All tests PASSED! Chinese search functionality is working correctly.
```

## What Gets Tested

1. **Chinese Character Detection** (8 tests)
   - Pure Chinese: "人脸识别", "技术"
   - Pure English: "AI", "Cyberpunk"
   - Mixed: "人工智能AI", "Technology技术"
   - With numbers and special chars

2. **Search Method Selection** (3 tests)
   - Verifies LIKE is used for Chinese
   - Verifies FTS5 is used for English
   - Verifies LIKE is used for mixed queries

3. **Chinese Search Functionality** (4 tests)
   - Tests: "人脸识别", "技术", "安全", "网络"
   - Verifies results are returned and contain search terms

4. **English FTS5 Search** (4 tests)
   - Tests: "AI", "Cyberpunk", "technology", "security"
   - Verifies FTS5 full-text search works correctly

5. **Mixed Language Search** (2 tests)
   - Tests: "人工智能AI", "网络security"
   - Verifies mixed queries use LIKE method

6. **Special Character Handling** (4 tests)
   - Tests queries don't cause errors with: !@#, ", -
   - Both Chinese and English contexts

## Test Files

- `test_chinese_search.py` - Main test suite (executable)
- `test_chinese_search_results.txt` - Last test run output
- `CHINESE_SEARCH_TEST_REPORT.md` - Detailed test report
- `RUN_CHINESE_SEARCH_TESTS.md` - This file

## Manual API Testing

You can also test the search API manually:

```bash
# Start the Flask app
python app.py

# In another terminal, test with curl:
curl "http://localhost:5000/api/search?q=人脸识别"
curl "http://localhost:5000/api/search?q=AI"
curl "http://localhost:5000/api/search?q=技术"
```

## Database Requirements

- Database must exist at `data/database.db`
- Must have `weibos`, `users`, and `weibos_fts` tables
- Should have actual content for meaningful tests

## Troubleshooting

If tests fail:
1. Verify database exists: `ls -lh data/database.db`
2. Check database has data: `sqlite3 data/database.db "SELECT COUNT(*) FROM weibos"`
3. Verify FTS table exists: `sqlite3 data/database.db "SELECT name FROM sqlite_master WHERE type='table' AND name='weibos_fts'"`

## Success Criteria

All tests should pass (25/25). The test verifies:
- Chinese character detection works correctly
- Search method selection is appropriate
- Chinese queries return results
- English queries work with FTS5
- No errors occur with special characters
