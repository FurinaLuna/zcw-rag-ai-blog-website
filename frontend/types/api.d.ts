// ============================================================
// API Type Definitions
// Generated from backend/app/schemas/*.py (Pydantic models)
// ============================================================

// ---- Generic Response Wrappers ----

/** Standard API response envelope used by all endpoints */
interface ApiResponse<T> {
  success: boolean
  data: T
  message: string
}

/** Paginated response data structure */
interface PaginatedData<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

/** Semantic search result item */
interface SemanticSearchItem extends ArticleListResponse {
  relevance: number
  snippet: string
}

// ---- Category Types ----

interface CategorySimple {
  id: number
  name: string
  slug: string
  type: string
}

interface CategoryResponse {
  id: number
  name: string
  slug: string
  type: string
  description: string | null
  cover_url: string | null
  sort_order: number
  article_count: number
  created_at: string
}

interface CategoryCreate {
  name: string
  slug: string
  description?: string | null
  cover_url?: string | null
  sort_order?: number
  type?: string
}

interface CategoryUpdate {
  name?: string | null
  slug?: string | null
  type?: string | null
  description?: string | null
  cover_url?: string | null
  sort_order?: number | null
}

interface SortOrderItem {
  id: number
  sort_order: number
}

interface SortOrderRequest {
  items: SortOrderItem[]
}

// ---- Tag Types ----

interface TagResponse {
  id: number
  name: string
  article_count: number
  created_at: string
}

interface TagCreate {
  name: string
}

// ---- Article Types ----

interface ArticleListResponse {
  id: number
  title: string
  summary: string | null
  slug: string
  cover_url: string | null
  category: CategorySimple | null
  tags: TagResponse[]
  view_count: number
  reading_time: number
  published_at: string | null
  created_at: string
  relevance?: number
  snippet?: string
}

interface ArticleDetailResponse {
  id: number
  title: string
  summary: string | null
  slug: string
  content_md: string | null
  cover_url: string | null
  category: CategorySimple | null
  tags: TagResponse[]
  view_count: number
  reading_time: number
  comment_count: number
  seo_title: string | null
  seo_description: string | null
  published_at: string | null
  created_at: string
  updated_at: string
  related_articles: ArticleListResponse[]
}

interface ArticleAdminResponse {
  id: number
  title: string
  summary: string | null
  slug: string
  content_md: string | null
  cover_url: string | null
  category: CategorySimple | null
  tags: TagResponse[]
  status: string
  vector_status: string
  view_count: number
  reading_time: number
  seo_title: string | null
  seo_description: string | null
  published_at: string | null
  created_at: string
  updated_at: string
}

interface ArticleCreate {
  title: string
  summary?: string | null
  slug: string
  content_md?: string | null
  cover_url?: string | null
  category_id?: number | null
  tag_ids?: number[]
  seo_title?: string | null
  seo_description?: string | null
}

interface ArticleUpdate {
  title?: string | null
  summary?: string | null
  slug?: string | null
  content_md?: string | null
  cover_url?: string | null
  category_id?: number | null
  tag_ids?: number[] | null
  seo_title?: string | null
  seo_description?: string | null
}

interface SlugCheckRequest {
  slug: string
  exclude_id?: number | null
}

interface SlugCheckResponse {
  available: boolean
}

// ---- Auth Types ----

interface LoginRequest {
  username: string
  password: string
}

interface TokenResponse {
  access_token: string
  token_type: string
}

interface AdminInfo {
  id: number
  username: string
  created_at: string
  last_login_at: string | null
}

// ---- Comment Types ----

interface CommentCreate {
  nickname: string
  content: string
  parent_id?: number | null
}

interface CommentResponse {
  id: number
  article_id: number
  nickname: string
  content: string
  likes: number
  parent_id: number | null
  created_at: string
}

// ---- RAG Types ----

interface AskRequest {
  question: string
}

interface SourceInfo {
  article_id: number
  article_title: string
  article_slug: string
  chunk_content: string
  similarity: number
}

interface AskResponse {
  answer: string
  sources: SourceInfo[]
  question: string
}

// ---- Dashboard Types ----

interface TodayOverview {
  pv: number
  uv: number
  rag_questions: number
  avg_lcp?: number | null
  error_count: number
}

interface TrendItem {
  date: string
  pv: number
  uv: number
}

interface HotArticle {
  id: number
  title: string
  slug: string
  view_count: number
  comment_count: number
}

interface KnowledgeStatus {
  total_articles: number
  synced: number
  syncing: number
  pending: number
  failed: number
  total_chunks: number
}

// ---- Home Data ----

interface HomeMetrics {
  total_articles: number
  total_chunks: number
}

interface HomeData {
  featured_articles: ArticleListResponse[]
  topics: CategoryResponse[]
  metrics: HomeMetrics
}

// ---- Monitor Types ----

interface MonitorEvent {
  event_type: string
  page_url: string
  event_data: Record<string, unknown>
  session_id?: string | null
}

interface MonitorBatchRequest {
  events: MonitorEvent[]
}

interface MonitorQuery {
  event_type?: string | null
  page_url?: string | null
  start_time?: string | null
  end_time?: string | null
  page?: number
  page_size?: number
}

interface MonitorLogResponse {
  id: number
  event_type: string
  page_url: string
  event_data: Record<string, any>
  session_id: string | null
  client_ip: string | null
  created_at: string
}

// ---- Knowledge Article (admin knowledge list) ----

interface KnowledgeArticleItem {
  id: number
  title: string
  slug: string
  status: string
  vector_status: string
}
