"""
Data Analyzer Tool - Enhanced BASED GOD CLI
Intelligent data analysis with multiple format support
"""

import json
import csv
import io
import re
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
import statistics

from .base_tool import BaseTool, ToolResponse, ToolStatus

class DataAnalyzerTool(BaseTool):
    """
    Advanced data analysis tool with multiple format support
    """
    
    def __init__(self):
        super().__init__(
            name="Data Analyzer",
            description="Intelligent data analysis supporting CSV, JSON, text, and structured data with statistical insights",
            capabilities=[
                "CSV data analysis with statistical summaries",
                "JSON data structure analysis and validation",
                "Text data pattern analysis and extraction",
                "Statistical calculations (mean, median, mode, etc.)",
                "Data quality assessment and cleaning suggestions",
                "Trend analysis and anomaly detection"
            ]
        )
        self.supported_formats = ["csv", "json", "text", "tsv", "xml"]
    
    async def execute(self, **kwargs) -> ToolResponse:
        """Execute data analysis"""
        
        data = kwargs.get("data")
        data_format = kwargs.get("format", "auto").lower()
        analysis_type = kwargs.get("analysis_type", "comprehensive")
        include_statistics = kwargs.get("include_statistics", True)
        include_quality_check = kwargs.get("include_quality_check", True)
        
        if not data:
            return ToolResponse(
                success=False,
                message="Data parameter is required",
                status=ToolStatus.FAILED
            )
        
        try:
            # Auto-detect format if needed
            if data_format == "auto":
                data_format = self._detect_format(data)
            
            # Parse data based on format
            parsed_data = self._parse_data(data, data_format)
            
            # Perform analysis
            analysis_results = self._analyze_data(
                parsed_data, analysis_type, include_statistics, include_quality_check
            )
            
            return ToolResponse(
                success=True,
                message=f"Successfully analyzed {data_format} data",
                data={
                    "format": data_format,
                    "analysis_type": analysis_type,
                    "results": analysis_results,
                    "data_summary": self._get_data_summary(parsed_data)
                },
                metadata={
                    "analyzed_at": datetime.now().isoformat(),
                    "data_size": len(str(data)),
                    "record_count": analysis_results.get("record_count", 0)
                }
            )
            
        except Exception as e:
            return ToolResponse(
                success=False,
                message=f"Data analysis failed: {str(e)}",
                status=ToolStatus.FAILED
            )
    
    def get_schema(self) -> Dict[str, Any]:
        """Get parameter schema for data analyzer"""
        return {
            "type": "object",
            "properties": {
                "data": {
                    "type": "string",
                    "description": "Data to analyze (as string)"
                },
                "format": {
                    "type": "string",
                    "enum": ["auto"] + self.supported_formats,
                    "description": "Data format (auto-detection if 'auto')",
                    "default": "auto"
                },
                "analysis_type": {
                    "type": "string",
                    "enum": ["comprehensive", "statistical", "structural", "quality", "patterns"],
                    "description": "Type of analysis to perform",
                    "default": "comprehensive"
                },
                "include_statistics": {
                    "type": "boolean",
                    "description": "Include statistical analysis",
                    "default": True
                },
                "include_quality_check": {
                    "type": "boolean",
                    "description": "Include data quality assessment",
                    "default": True
                }
            },
            "required": ["data"]
        }
    
    def _detect_format(self, data: str) -> str:
        """Auto-detect data format"""
        
        # Try JSON first
        try:
            json.loads(data)
            return "json"
        except Exception as e:
            pass
        
        # Check for CSV patterns
        if ',' in data and '\n' in data:
            lines = data.strip().split('\n')
            if len(lines) > 1:
                # Check if first line looks like headers
                first_line = lines[0]
                if ',' in first_line and not first_line.startswith('{'):
                    return "csv"
        
        # Check for TSV patterns
        if '\t' in data and '\n' in data:
            return "tsv"
        
        # Check for XML
        if data.strip().startswith('<') and data.strip().endswith('>'):
            return "xml"
        
        # Default to text
        return "text"
    
    def _parse_data(self, data: str, data_format: str) -> Union[List[Dict], Dict, List[str]]:
        """Parse data based on format"""
        
        if data_format == "json":
            return json.loads(data)
        
        elif data_format == "csv":
            return self._parse_csv(data)
        
        elif data_format == "tsv":
            return self._parse_csv(data, delimiter='\t')
        
        elif data_format == "text":
            return data.split('\n')
        
        elif data_format == "xml":
            # Basic XML parsing (would need proper XML parser for production)
            return {"xml_content": data, "note": "Basic XML parsing - needs proper parser"}
        
        else:
            raise ValueError(f"Unsupported format: {data_format}")
    
    def _parse_csv(self, data: str, delimiter: str = ',') -> List[Dict]:
        """Parse CSV data into list of dictionaries"""
        
        reader = csv.DictReader(io.StringIO(data), delimiter=delimiter)
        return list(reader)
    
    def _analyze_data(self, parsed_data: Union[List[Dict], Dict, List[str]], 
                     analysis_type: str, include_statistics: bool, 
                     include_quality_check: bool) -> Dict[str, Any]:
        """Perform comprehensive data analysis"""
        
        results = {}
        
        if analysis_type in ["comprehensive", "structural"]:
            results["structure"] = self._analyze_structure(parsed_data)
        
        if analysis_type in ["comprehensive", "statistical"] and include_statistics:
            results["statistics"] = self._analyze_statistics(parsed_data)
        
        if analysis_type in ["comprehensive", "quality"] and include_quality_check:
            results["quality"] = self._analyze_quality(parsed_data)
        
        if analysis_type in ["comprehensive", "patterns"]:
            results["patterns"] = self._analyze_patterns(parsed_data)
        
        results["record_count"] = self._get_record_count(parsed_data)
        
        return results
    
    def _analyze_structure(self, data: Union[List[Dict], Dict, List[str]]) -> Dict[str, Any]:
        """Analyze data structure"""
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # CSV-like data
            columns = list(data[0].keys()) if data else []
            
            return {
                "type": "tabular",
                "columns": columns,
                "column_count": len(columns),
                "row_count": len(data),
                "column_types": self._infer_column_types(data, columns)
            }
        
        elif isinstance(data, dict):
            # JSON object
            return {
                "type": "object",
                "keys": list(data.keys()),
                "key_count": len(data),
                "nested_structure": self._analyze_nested_structure(data)
            }
        
        elif isinstance(data, list):
            # List of strings or other data
            return {
                "type": "list",
                "item_count": len(data),
                "item_types": self._analyze_list_item_types(data),
                "average_length": statistics.mean(len(str(item)) for item in data) if data else 0
            }
        
        else:
            return {
                "type": "unknown",
                "data_type": type(data).__name__
            }
    
    def _analyze_statistics(self, data: Union[List[Dict], Dict, List[str]]) -> Dict[str, Any]:
        """Perform statistical analysis"""
        
        stats = {}
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Tabular data statistics
            columns = list(data[0].keys())
            
            for column in columns:
                values = [row.get(column) for row in data]
                numeric_values = self._extract_numeric_values(values)
                
                if numeric_values:
                    stats[column] = {
                        "count": len(numeric_values),
                        "mean": statistics.mean(numeric_values),
                        "median": statistics.median(numeric_values),
                        "min": min(numeric_values),
                        "max": max(numeric_values),
                        "std_dev": statistics.stdev(numeric_values) if len(numeric_values) > 1 else 0
                    }
                else:
                    # String data statistics
                    non_empty_values = [v for v in values if v and str(v).strip()]
                    stats[column] = {
                        "count": len(non_empty_values),
                        "unique_values": len(set(str(v) for v in non_empty_values)),
                        "most_common": self._get_most_common(non_empty_values),
                        "average_length": statistics.mean(len(str(v)) for v in non_empty_values) if non_empty_values else 0
                    }
        
        elif isinstance(data, list):
            # List statistics
            numeric_values = self._extract_numeric_values(data)
            
            if numeric_values:
                stats["numeric_analysis"] = {
                    "count": len(numeric_values),
                    "mean": statistics.mean(numeric_values),
                    "median": statistics.median(numeric_values),
                    "min": min(numeric_values),
                    "max": max(numeric_values)
                }
            
            stats["text_analysis"] = {
                "total_items": len(data),
                "average_length": statistics.mean(len(str(item)) for item in data) if data else 0,
                "unique_items": len(set(str(item) for item in data))
            }
        
        return stats
    
    def _analyze_quality(self, data: Union[List[Dict], Dict, List[str]]) -> Dict[str, Any]:
        """Analyze data quality"""
        
        quality_issues = []
        recommendations = []
        
        if isinstance(data, list) and data and isinstance(data[0], dict):
            # Check for missing values
            columns = list(data[0].keys())
            
            for column in columns:
                missing_count = sum(1 for row in data if not row.get(column) or str(row.get(column)).strip() == '')
                missing_percentage = (missing_count / len(data)) * 100
                
                if missing_percentage > 10:
                    quality_issues.append(f"Column '{column}' has {missing_percentage:.1f}% missing values")
                    recommendations.append(f"Consider filling or removing missing values in '{column}'")
            
            # Check for duplicate rows
            seen_rows = set()
            duplicates = 0
            for row in data:
                row_str = str(sorted(row.items()))
                if row_str in seen_rows:
                    duplicates += 1
                seen_rows.add(row_str)
            
            if duplicates > 0:
                quality_issues.append(f"Found {duplicates} duplicate rows")
                recommendations.append("Consider removing duplicate rows")
        
        elif isinstance(data, list):
            # Check for empty items
            empty_items = sum(1 for item in data if not item or str(item).strip() == '')
            if empty_items > 0:
                quality_issues.append(f"Found {empty_items} empty items")
                recommendations.append("Consider removing empty items")
        
        return {
            "issues": quality_issues,
            "recommendations": recommendations,
            "quality_score": max(0, 100 - len(quality_issues) * 10)  # Simple scoring
        }
    
    def _analyze_patterns(self, data: Union[List[Dict], Dict, List[str]]) -> Dict[str, Any]:
        """Analyze patterns in the data"""
        
        patterns = {}
        
        if isinstance(data, list):
            # Look for common patterns
            text_data = [str(item) for item in data]
            
            # Email pattern
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            emails = [re.findall(email_pattern, text) for text in text_data]
            email_count = sum(len(email_list) for email_list in emails)
            
            # Phone pattern (simple)
            phone_pattern = r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b'
            phones = [re.findall(phone_pattern, text) for text in text_data]
            phone_count = sum(len(phone_list) for phone_list in phones)
            
            # URL pattern
            url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            urls = [re.findall(url_pattern, text) for text in text_data]
            url_count = sum(len(url_list) for url_list in urls)
            
            patterns = {
                "emails_found": email_count,
                "phones_found": phone_count,
                "urls_found": url_count,
                "common_words": self._get_common_words(text_data)
            }
        
        return patterns
    
    def _get_record_count(self, data: Union[List[Dict], Dict, List[str]]) -> int:
        """Get the number of records in the data"""
        
        if isinstance(data, list):
            return len(data)
        elif isinstance(data, dict):
            return 1
        else:
            return 0
    
    def _get_data_summary(self, data: Union[List[Dict], Dict, List[str]]) -> Dict[str, Any]:
        """Get a summary of the data"""
        
        return {
            "data_type": type(data).__name__,
            "size": len(str(data)),
            "record_count": self._get_record_count(data),
            "preview": str(data)[:200] + "..." if len(str(data)) > 200 else str(data)
        }
    
    def _infer_column_types(self, data: List[Dict], columns: List[str]) -> Dict[str, str]:
        """Infer column data types"""
        
        column_types = {}
        
        for column in columns:
            values = [row.get(column) for row in data[:100]]  # Sample first 100 rows
            
            # Check if numeric
            numeric_values = self._extract_numeric_values(values)
            if len(numeric_values) > len(values) * 0.8:  # 80% numeric
                column_types[column] = "numeric"
            else:
                column_types[column] = "text"
        
        return column_types
    
    def _extract_numeric_values(self, values: List) -> List[float]:
        """Extract numeric values from a list"""
        
        numeric_values = []
        
        for value in values:
            if value is None:
                continue
            
            try:
                # Try direct conversion
                numeric_values.append(float(value))
            except (ValueError, TypeError):
                # Try to extract numbers from strings
                if isinstance(value, str):
                    # Remove common non-numeric characters
                    cleaned = re.sub(r'[^\d.-]', '', value)
                    try:
                        if cleaned:
                            numeric_values.append(float(cleaned))
                    except ValueError:
                        continue
        
        return numeric_values
    
    def _analyze_nested_structure(self, obj: Dict, depth: int = 0) -> Dict[str, Any]:
        """Analyze nested structure of JSON object"""
        
        if depth > 3:  # Limit recursion depth
            return {"max_depth_reached": True}
        
        structure = {}
        
        for key, value in obj.items():
            if isinstance(value, dict):
                structure[key] = {
                    "type": "object",
                    "keys": len(value),
                    "nested": self._analyze_nested_structure(value, depth + 1)
                }
            elif isinstance(value, list):
                structure[key] = {
                    "type": "array",
                    "length": len(value),
                    "item_types": self._analyze_list_item_types(value[:10])  # Sample first 10
                }
            else:
                structure[key] = {
                    "type": type(value).__name__
                }
        
        return structure
    
    def _analyze_list_item_types(self, items: List) -> Dict[str, int]:
        """Analyze types of items in a list"""
        
        type_counts = {}
        
        for item in items:
            item_type = type(item).__name__
            type_counts[item_type] = type_counts.get(item_type, 0) + 1
        
        return type_counts
    
    def _get_most_common(self, values: List, limit: int = 5) -> List[tuple]:
        """Get most common values"""
        
        from collections import Counter
        counter = Counter(str(v) for v in values)
        return counter.most_common(limit)
    
    def _get_common_words(self, text_data: List[str], limit: int = 10) -> List[tuple]:
        """Get most common words from text data"""
        
        from collections import Counter
        
        # Extract words
        all_words = []
        for text in text_data:
            words = re.findall(r'\b[a-zA-Z]{3,}\b', text.lower())  # Words with 3+ letters
            all_words.extend(words)
        
        # Filter out common stop words
        stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'its', 'may', 'new', 'now', 'old', 'see', 'two', 'who', 'boy', 'did', 'man', 'way', 'use'}
        
        filtered_words = [word for word in all_words if word not in stop_words]
        
        counter = Counter(filtered_words)
        return counter.most_common(limit)