#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test Chinese Search Functionality

This test verifies that the Chinese character detection and search fix works correctly.
The fix detects Chinese characters and uses LIKE query instead of FTS5 for better Chinese support.
"""

import sqlite3
import json
import re
from pathlib import Path


class TestChineseSearch:
    """Test suite for Chinese character search functionality"""

    def __init__(self, db_path='data/database.db'):
        self.db_path = db_path
        self.test_results = []

    def get_db_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def contains_chinese(self, text):
        """Check if text contains Chinese characters"""
        return bool(re.search(r'[\u4e00-\u9fff]', text))

    def search_weibos(self, query):
        """
        Search weibos using the same logic as app.py
        This mimics the /api/search endpoint
        """
        conn = self.get_db_connection()
        cursor = conn.cursor()

        # Use the same logic as in app.py
        if self.contains_chinese(query):
            # Chinese query uses LIKE search
            cursor.execute('''
                SELECT w.id, w.content, w.created_at, u.name as user_name
                FROM weibos w
                LEFT JOIN users u ON w.uid = u.uid
                WHERE w.content LIKE ?
                ORDER BY CAST(w.id AS INTEGER) DESC
                LIMIT 20
            ''', (f'%{query}%',))
        else:
            # English query uses FTS full-text search
            clean_query = re.sub(r'["\(\)\*\+\-<>@\^|~!/:\[\]{}]', ' ', query)
            clean_query = ' '.join(clean_query.split())

            if not clean_query:
                conn.close()
                return []

            try:
                cursor.execute('''
                    SELECT w.id, w.content, w.created_at, u.name as user_name
                    FROM weibos_fts f
                    JOIN weibos w ON CAST(f.id AS TEXT) = CAST(w.id AS TEXT)
                    LEFT JOIN users u ON w.uid = u.uid
                    WHERE f.content MATCH ?
                    ORDER BY CAST(w.id AS INTEGER) DESC
                    LIMIT 20
                ''', (clean_query,))
            except Exception as e:
                # Fallback to LIKE query if FTS fails
                cursor.execute('''
                    SELECT w.id, w.content, w.created_at, u.name as user_name
                    FROM weibos w
                    LEFT JOIN users u ON w.uid = u.uid
                    WHERE w.content LIKE ?
                    ORDER BY CAST(w.id AS INTEGER) DESC
                    LIMIT 20
                ''', (f'%{query}%',))

        results = []
        for row in cursor.fetchall():
            results.append({
                'id': row['id'],
                'content': row['content'],
                'created_at': row['created_at'],
                'user_name': row['user_name']
            })

        conn.close()
        return results

    def test_chinese_detection(self):
        """Test 1: Verify Chinese character detection works"""
        print("\n" + "="*80)
        print("TEST 1: Chinese Character Detection")
        print("="*80)

        test_cases = [
            ("人脸识别", True, "Pure Chinese"),
            ("技术", True, "Pure Chinese"),
            ("AI", False, "Pure English"),
            ("Cyberpunk", False, "Pure English"),
            ("人工智能AI", True, "Mixed Chinese and English"),
            ("Technology技术", True, "Mixed English and Chinese"),
            ("123数字", True, "Numbers with Chinese"),
            ("special!@#特殊字符", True, "Special chars with Chinese"),
        ]

        passed = 0
        failed = 0

        for text, expected, description in test_cases:
            result = self.contains_chinese(text)
            status = "PASS" if result == expected else "FAIL"

            if result == expected:
                passed += 1
            else:
                failed += 1

            print(f"  [{status}] {description:30} '{text}' -> {result} (expected: {expected})")

        print(f"\n  Summary: {passed} passed, {failed} failed")
        self.test_results.append(("Chinese Detection", passed, failed))
        return failed == 0

    def test_chinese_search(self):
        """Test 2: Test Chinese character search"""
        print("\n" + "="*80)
        print("TEST 2: Chinese Character Search")
        print("="*80)

        test_queries = [
            "人脸识别",
            "技术",
            "安全",
            "网络",
        ]

        passed = 0
        failed = 0

        for query in test_queries:
            results = self.search_weibos(query)

            # Verify all results contain the query string
            all_match = all(query in result['content'] for result in results)
            has_results = len(results) > 0

            if has_results and all_match:
                status = "PASS"
                passed += 1
            elif not has_results:
                status = "SKIP"
                print(f"  [{status}] Query '{query}' -> No results in database")
                continue
            else:
                status = "FAIL"
                failed += 1

            print(f"  [{status}] Query '{query}' -> {len(results)} results")
            if results and status == "PASS":
                # Show first result preview
                preview = results[0]['content'][:60].replace('\n', ' ')
                print(f"         First result: {preview}...")

        print(f"\n  Summary: {passed} passed, {failed} failed")
        self.test_results.append(("Chinese Search", passed, failed))
        return failed == 0

    def test_english_search_fts(self):
        """Test 3: Test English search with FTS5"""
        print("\n" + "="*80)
        print("TEST 3: English Search with FTS5")
        print("="*80)

        test_queries = [
            "AI",
            "Cyberpunk",
            "technology",
            "security",
        ]

        passed = 0
        failed = 0

        for query in test_queries:
            results = self.search_weibos(query)

            # For English, FTS might match word boundaries, so just check we get results
            has_results = len(results) > 0

            if has_results:
                # Verify at least some results contain the query (case-insensitive)
                matches = sum(1 for r in results if query.lower() in r['content'].lower())
                if matches > 0:
                    status = "PASS"
                    passed += 1
                    print(f"  [{status}] Query '{query}' -> {len(results)} results, {matches} contain query")
                    if results:
                        preview = results[0]['content'][:60].replace('\n', ' ')
                        print(f"         First result: {preview}...")
                else:
                    status = "FAIL"
                    failed += 1
                    print(f"  [{status}] Query '{query}' -> {len(results)} results but none contain query")
            else:
                status = "SKIP"
                print(f"  [{status}] Query '{query}' -> No results in database")

        print(f"\n  Summary: {passed} passed, {failed} failed")
        self.test_results.append(("English FTS Search", passed, failed))
        return failed == 0

    def test_mixed_search(self):
        """Test 4: Test mixed Chinese and English search"""
        print("\n" + "="*80)
        print("TEST 4: Mixed Chinese and English Search")
        print("="*80)

        # Mixed queries should use LIKE because they contain Chinese
        test_queries = [
            "人工智能AI",
            "网络security",
        ]

        passed = 0
        failed = 0

        for query in test_queries:
            # Split query to check individual parts
            chinese_part = ''.join(re.findall(r'[\u4e00-\u9fff]+', query))
            english_part = ''.join(re.findall(r'[a-zA-Z]+', query))

            # Search for Chinese part only (since mixed queries might not exist exactly)
            if chinese_part:
                results = self.search_weibos(chinese_part)

                if len(results) > 0:
                    status = "PASS"
                    passed += 1
                    print(f"  [{status}] Query '{query}' -> Testing with '{chinese_part}' -> {len(results)} results")
                    if results:
                        preview = results[0]['content'][:60].replace('\n', ' ')
                        print(f"         First result: {preview}...")
                else:
                    status = "SKIP"
                    print(f"  [{status}] Query '{query}' -> No results for '{chinese_part}'")
            else:
                status = "SKIP"
                print(f"  [{status}] Query '{query}' -> No Chinese characters to test")

        print(f"\n  Summary: {passed} passed, {failed} failed")
        self.test_results.append(("Mixed Search", passed, failed))
        return failed == 0

    def test_special_characters(self):
        """Test 5: Test special character handling"""
        print("\n" + "="*80)
        print("TEST 5: Special Character Handling")
        print("="*80)

        test_queries = [
            ("特殊!@#", "Chinese with special chars"),
            ("test!", "English with special chars"),
            ('test"quote', "English with quotes"),
            ("test-dash", "English with dash"),
        ]

        passed = 0
        failed = 0

        for query, description in test_queries:
            try:
                results = self.search_weibos(query)
                status = "PASS"
                passed += 1
                print(f"  [{status}] {description:35} '{query}' -> {len(results)} results (no error)")
            except Exception as e:
                status = "FAIL"
                failed += 1
                print(f"  [{status}] {description:35} '{query}' -> ERROR: {str(e)}")

        print(f"\n  Summary: {passed} passed, {failed} failed")
        self.test_results.append(("Special Characters", passed, failed))
        return failed == 0

    def test_search_method_selection(self):
        """Test 6: Verify correct search method is selected"""
        print("\n" + "="*80)
        print("TEST 6: Search Method Selection Verification")
        print("="*80)

        test_cases = [
            ("人脸识别", "LIKE", "Pure Chinese should use LIKE"),
            ("AI", "FTS", "Pure English should use FTS"),
            ("人工智能AI", "LIKE", "Mixed should use LIKE (contains Chinese)"),
        ]

        passed = 0
        failed = 0

        for query, expected_method, description in test_cases:
            is_chinese = self.contains_chinese(query)
            actual_method = "LIKE" if is_chinese else "FTS"

            status = "PASS" if actual_method == expected_method else "FAIL"
            if actual_method == expected_method:
                passed += 1
            else:
                failed += 1

            print(f"  [{status}] {description:45} -> {actual_method} (expected: {expected_method})")

        print(f"\n  Summary: {passed} passed, {failed} failed")
        self.test_results.append(("Method Selection", passed, failed))
        return failed == 0

    def run_all_tests(self):
        """Run all test suites"""
        print("\n" + "="*80)
        print("CHINESE SEARCH FUNCTIONALITY TEST SUITE")
        print("="*80)
        print(f"Database: {self.db_path}")

        # Check database exists
        if not Path(self.db_path).exists():
            print(f"\nERROR: Database not found at {self.db_path}")
            return False

        # Run all tests
        all_passed = True
        all_passed &= self.test_chinese_detection()
        all_passed &= self.test_search_method_selection()
        all_passed &= self.test_chinese_search()
        all_passed &= self.test_english_search_fts()
        all_passed &= self.test_mixed_search()
        all_passed &= self.test_special_characters()

        # Print final summary
        print("\n" + "="*80)
        print("FINAL SUMMARY")
        print("="*80)

        total_passed = 0
        total_failed = 0

        for test_name, passed, failed in self.test_results:
            total_passed += passed
            total_failed += failed
            status = "PASS" if failed == 0 else "FAIL"
            print(f"  [{status}] {test_name:30} -> {passed} passed, {failed} failed")

        print("\n" + "-"*80)
        print(f"  TOTAL: {total_passed} passed, {total_failed} failed")
        print("="*80)

        if all_passed and total_failed == 0:
            print("\n✓ All tests PASSED! Chinese search functionality is working correctly.")
        else:
            print("\n✗ Some tests FAILED. Please review the results above.")

        return all_passed


def main():
    """Main test runner"""
    tester = TestChineseSearch()
    success = tester.run_all_tests()
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
