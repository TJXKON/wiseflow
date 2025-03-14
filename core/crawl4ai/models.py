# from re import U
from pydantic import BaseModel, HttpUrl
from typing import List, Dict, Optional, Callable, Awaitable, Union, Any
from enum import Enum
from dataclasses import dataclass
from .ssl_certificate import SSLCertificate
from datetime import datetime
from datetime import timedelta


###############################
# Dispatcher Models
###############################
@dataclass
class DomainState:
    last_request_time: float = 0
    current_delay: float = 0
    fail_count: int = 0


@dataclass
class CrawlerTaskResult:
    task_id: str
    url: str
    result: "CrawlResult"
    memory_usage: float
    peak_memory: float
    start_time: Union[datetime, float]
    end_time: Union[datetime, float]
    error_message: str = ""


class CrawlStatus(Enum):
    QUEUED = "QUEUED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# @dataclass
# class CrawlStats:
#     task_id: str
#     url: str
#     status: CrawlStatus
#     start_time: Optional[datetime] = None
#     end_time: Optional[datetime] = None
#     memory_usage: float = 0.0
#     peak_memory: float = 0.0
#     error_message: str = ""

#     @property
#     def duration(self) -> str:
#         if not self.start_time:
#             return "0:00"
#         end = self.end_time or datetime.now()
#         duration = end - self.start_time
#         return str(timedelta(seconds=int(duration.total_seconds())))


@dataclass
class CrawlStats:
    task_id: str
    url: str
    status: CrawlStatus
    start_time: Optional[Union[datetime, float]] = None
    end_time: Optional[Union[datetime, float]] = None
    memory_usage: float = 0.0
    peak_memory: float = 0.0
    error_message: str = ""

    @property
    def duration(self) -> str:
        if not self.start_time:
            return "0:00"
            
        # Convert start_time to datetime if it's a float
        start = self.start_time
        if isinstance(start, float):
            start = datetime.fromtimestamp(start)
            
        # Get end time or use current time
        end = self.end_time or datetime.now()
        # Convert end_time to datetime if it's a float
        if isinstance(end, float):
            end = datetime.fromtimestamp(end)
            
        duration = end - start
        return str(timedelta(seconds=int(duration.total_seconds())))

class DisplayMode(Enum):
    DETAILED = "DETAILED"
    AGGREGATED = "AGGREGATED"


###############################
# Crawler Models
###############################
@dataclass
class TokenUsage:
    completion_tokens: int = 0
    prompt_tokens: int = 0
    total_tokens: int = 0
    completion_tokens_details: Optional[dict] = None
    prompt_tokens_details: Optional[dict] = None


class UrlModel(BaseModel):
    url: HttpUrl
    forced: bool = False


class MarkdownGenerationResult(BaseModel):
    raw_markdown: str
    markdown_with_citations: str
    references_markdown: str
    fit_markdown: Optional[str] = None
    fit_html: Optional[str] = None

    def __str__(self):
        return self.raw_markdown

@dataclass
class TraversalStats:
    """Statistics for the traversal process"""

    start_time: datetime = datetime.now()
    urls_processed: int = 0
    urls_failed: int = 0
    urls_skipped: int = 0
    total_depth_reached: int = 0
    current_depth: int = 0

class DispatchResult(BaseModel):
    task_id: str
    memory_usage: float
    peak_memory: float
    start_time: Union[datetime, float]
    end_time: Union[datetime, float]
    error_message: str = ""

class CrawlResult(BaseModel):
    url: str
    html: str
    success: bool
    cleaned_html: Optional[str] = None
    media: Dict[str, List[Dict]] = {}
    links: Dict[str, List[Dict]] = {}
    downloaded_files: Optional[List[str]] = None
    js_execution_result: Optional[Dict[str, Any]] = None
    screenshot: Optional[str] = None
    pdf: Optional[bytes] = None
    markdown: str = ''
    extracted_content: Optional[str] = None
    metadata: Optional[dict] = None
    error_message: Optional[str] = None
    session_id: Optional[str] = None
    response_headers: Optional[dict] = None
    status_code: Optional[int] = None
    ssl_certificate: Optional[SSLCertificate] = None
    dispatch_result: Optional[DispatchResult] = None
    redirected_url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

class StringCompatibleMarkdown(str):
    """A string subclass that also provides access to MarkdownGenerationResult attributes"""
    def __new__(cls, markdown_result):
        return super().__new__(cls, markdown_result.raw_markdown)
    
    def __init__(self, markdown_result):
        self._markdown_result = markdown_result
    
    def __getattr__(self, name):
        return getattr(self._markdown_result, name)

# END of backward compatibility code for markdown/markdown_v2.
# When removing this code in the future, make sure to:
# 1. Replace the private attribute and property with a standard field
# 2. Update any serialization logic that might depend on the current behavior

class AsyncCrawlResponse(BaseModel):
    html: str
    response_headers: Dict[str, str]
    js_execution_result: Optional[Dict[str, Any]] = None
    status_code: int
    screenshot: Optional[str] = None
    pdf_data: Optional[bytes] = None
    get_delayed_content: Optional[Callable[[Optional[float]], Awaitable[str]]] = None
    downloaded_files: Optional[List[str]] = None
    ssl_certificate: Optional[SSLCertificate] = None
    redirected_url: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True


###############################
# Scraping Models
###############################
class MediaItem(BaseModel):
    src: Optional[str] = ""
    data: Optional[str] = ""
    alt: Optional[str] = ""
    desc: Optional[str] = ""
    score: Optional[int] = 0
    type: str = "image"
    group_id: Optional[int] = 0
    format: Optional[str] = None
    width: Optional[int] = None


class Link(BaseModel):
    href: Optional[str] = ""
    text: Optional[str] = ""
    title: Optional[str] = ""
    base_domain: Optional[str] = ""


class Media(BaseModel):
    images: List[MediaItem] = []
    videos: List[
        MediaItem
    ] = []  # Using MediaItem model for now, can be extended with Video model if needed
    audios: List[
        MediaItem
    ] = []  # Using MediaItem model for now, can be extended with Audio model if needed


class Links(BaseModel):
    internal: List[Link] = []
    external: List[Link] = []


class ScrapingResult(BaseModel):
    cleaned_html: str
    success: bool
    media: Media = Media()
    links: Links = Links()
    metadata: Dict[str, Any] = {}
