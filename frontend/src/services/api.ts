// 导入 Axios HTTP 客户端库及其类型定义
import axios, { AxiosInstance, AxiosResponse } from "axios";
// 导入自定义的 API 错误类
import { ApiError } from "./errors";
// 导入所有 API 相关的 TypeScript 类型定义
import type {
  ApiResponse,           // 统一 API 响应格式
  CreateUserRequest,     // 创建用户请求体
  CreateUserResponse,    // 创建用户响应体
  ChatHistoryRequest,    // 聊天历史请求参数
  ChatHistoryResponse,   // 聊天历史响应数据
  ProjectInitRequest,    // 项目初始化请求体
  ProjectInitResponse,   // 项目初始化响应体
  SettingsResponse,      // 设置响应数据
  UpdateSettingsRequest, // 更新设置请求体
  UpdateSettingsResponse,// 更新设置响应体
  MemoryResponse,        // Memory 查询响应
  ToolCallRequest,       // 工具调用请求体
  ToolCallResponse,      // 工具调用响应体
} from "../types";

/**
 * API 客户端类
 * 封装所有与后端的 HTTP 通信，提供统一的接口调用方法
 */
class ApiClient {
  // Axios 实例，用于发送 HTTP 请求
  private client: AxiosInstance;

  /**
   * 构造函数
   * @param baseURL - 后端 API 的基础 URL，默认为本地开发服务器
   */
  constructor(baseURL: string = "http://localhost:8000") {
    // 创建 Axios 实例，配置默认参数
    this.client = axios.create({
      baseURL,                    // 基础 URL
      timeout: 30000,             // 请求超时时间：30秒
      headers: { "Content-Type": "application/json" },  // 默认请求头：JSON 格式
    });

    // 请求拦截器：在每个请求发送前执行（可用于添加 token 等）
    this.client.interceptors.request.use((config) => config);

    // 响应拦截器：处理响应错误
    this.client.interceptors.response.use(
      (response) => response,  // 成功响应直接返回
      (error) => {
        // 提取错误信息
        const endpoint = error.config?.url || "unknown";  // 请求的端点路径
        const code = error.response?.status || 0;          // HTTP 状态码
        const message = error.response?.data?.message || error.message;  // 错误消息
        // 包装为自定义 ApiError 并抛出
        return Promise.reject(new ApiError(message, code, endpoint));
      }
    );
  }

  /**
   * 发送 GET 请求
   * @param url - 请求路径
   * @param params - 查询参数
   * @returns 统一格式的 API 响应
   */
  private async get<T>(url: string, params?: object): Promise<ApiResponse<T>> {
    const response: AxiosResponse<ApiResponse<T>> = await this.client.get(url, { params });
    return response.data;  // 返回响应体数据
  }

  /**
   * 发送 POST 请求
   * @param url - 请求路径
   * @param data - 请求体数据
   * @returns 统一格式的 API 响应
   */
  private async post<T>(url: string, data?: object): Promise<ApiResponse<T>> {
    const response: AxiosResponse<ApiResponse<T>> = await this.client.post(url, data);
    return response.data;  // 返回响应体数据
  }

  /**
   * 创建新用户
   * @param username - 用户名
   * @param preferences - 用户偏好设置（可选）
   * @returns 创建的用户信息
   */
  async createUser(username: string, preferences?: object): Promise<ApiResponse<CreateUserResponse>> {
    return this.post("/api/users/create", { username, preferences } as CreateUserRequest);
  }

  /**
   * 获取聊天历史记录
   * @param sessionId - 会话 ID
   * @param limit - 返回数量限制（可选）
   * @param offset - 偏移量（可选）
   * @returns 聊天历史消息列表
   */
  async getChatHistory(sessionId: string, limit?: number, offset?: number): Promise<ApiResponse<ChatHistoryResponse>> {
    return this.get("/api/chat/history", { session_id: sessionId, limit, offset } as ChatHistoryRequest);
  }

  /**
   * 获取全部设置
   * @returns 所有设置项（模型、Agent、Memory、Workflow、RAG、Tool 六大类）
   */
  async getSettings(): Promise<ApiResponse<SettingsResponse>> {
    return this.get("/api/settings");
  }

  /**
   * 更新单个设置项
   * @param section - 设置分类（如"模型设置"）
   * @param key - 设置键名
   * @param value - 新的设置值
   * @returns 更新前后的值
   */
  async updateSettings(section: string, key: string, value: any): Promise<ApiResponse<UpdateSettingsResponse>> {
    return this.post("/api/settings", { section, key, value } as UpdateSettingsRequest);
  }

  /**
   * 获取指定层级的 Memory 内容
   * @param project - 项目名称
   * @param layer - Memory 层级（global/project/task/session/checkpoint/notes）
   * @returns Memory 内容和更新时间
   */
  async getMemory(project: string, layer: string): Promise<ApiResponse<MemoryResponse>> {
    return this.get("/api/memory", { project, layer });
  }

  /**
   * 调用后端工具
   * @param tool - 工具名称（如 read_file、write_file）
   * @param args - 工具参数
   * @returns 工具执行结果
   */
  async callTool(tool: string, args: Record<string, any>): Promise<ApiResponse<ToolCallResponse>> {
    return this.post("/api/tools/call", { tool, args } as ToolCallRequest);
  }

  /**
   * 初始化项目
   * @param projectName - 项目名称
   * @param path - 项目路径
   * @param language - 编程语言（可选）
   * @param framework - 框架（可选）
   * @returns 初始化结果，包含 .mimo 目录结构
   */
  async initProject(projectName: string, path: string, language?: string, framework?: string): Promise<ApiResponse<ProjectInitResponse>> {
    return this.post("/api/project/init", { project_name: projectName, path, language, framework } as ProjectInitRequest);
  }

  /**
   * 获取项目状态
   * @returns 项目信息（名称、版本、Agent 列表、Memory 层级、工具列表）
   */
  async getProjectStatus(): Promise<ApiResponse<Record<string, any>>> {
    return this.get("/api/project/status");
  }

  /**
   * 获取所有可用工具列表
   * @returns 工具定义数组（名称、描述、参数）
   */
  async listTools(): Promise<ApiResponse<Array<Record<string, any>>>> {
    return this.get("/api/tools/list");
  }

  /**
   * 搜索 Memory 内容
   * @param query - 搜索关键词
   * @param limit - 返回数量限制（可选）
   * @returns 搜索结果数组，包含相关度分数
   */
  async searchMemory(query: string, limit?: number): Promise<ApiResponse<Array<Record<string, any>>>> {
    return this.get("/api/memory/search", { query, limit });
  }

  /**
   * 重新加载设置文件
   * @returns 操作结果
   */
  async reloadSettings(): Promise<ApiResponse<null>> {
    return this.post("/api/settings/reload");
  }
}

// 导出全局唯一的 API 客户端实例
export const api = new ApiClient();
