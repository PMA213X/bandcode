import axios, { AxiosInstance, AxiosResponse } from "axios";
import { ApiError } from "./errors";
import type {
  ApiResponse,
  CreateUserRequest,
  CreateUserResponse,
  ChatHistoryRequest,
  ChatHistoryResponse,
  ProjectInitRequest,
  ProjectInitResponse,
  SettingsResponse,
  UpdateSettingsRequest,
  UpdateSettingsResponse,
  MemoryResponse,
  ToolCallRequest,
  ToolCallResponse,
} from "../types";

class ApiClient {
  private client: AxiosInstance;

  constructor(baseURL: string = "http://localhost:8000") {
    this.client = axios.create({
      baseURL,
      timeout: 30000,
      headers: { "Content-Type": "application/json" },
    });

    this.client.interceptors.request.use((config) => config);

    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        const endpoint = error.config?.url || "unknown";
        const code = error.response?.status || 0;
        const message = error.response?.data?.message || error.message;
        return Promise.reject(new ApiError(message, code, endpoint));
      }
    );
  }

  private async get<T>(url: string, params?: object): Promise<ApiResponse<T>> {
    const response: AxiosResponse<ApiResponse<T>> = await this.client.get(url, { params });
    return response.data;
  }

  private async post<T>(url: string, data?: object): Promise<ApiResponse<T>> {
    const response: AxiosResponse<ApiResponse<T>> = await this.client.post(url, data);
    return response.data;
  }

  async createUser(username: string, preferences?: object): Promise<ApiResponse<CreateUserResponse>> {
    return this.post("/api/users/create", { username, preferences } as CreateUserRequest);
  }

  async getChatHistory(sessionId: string, limit?: number, offset?: number): Promise<ApiResponse<ChatHistoryResponse>> {
    return this.get("/api/chat/history", { session_id: sessionId, limit, offset } as ChatHistoryRequest);
  }

  async getSettings(): Promise<ApiResponse<SettingsResponse>> {
    return this.get("/api/settings");
  }

  async updateSettings(section: string, key: string, value: any): Promise<ApiResponse<UpdateSettingsResponse>> {
    return this.post("/api/settings", { section, key, value } as UpdateSettingsRequest);
  }

  async getMemory(project: string, layer: string): Promise<ApiResponse<MemoryResponse>> {
    return this.get("/api/memory", { project, layer });
  }

  async callTool(tool: string, args: Record<string, any>): Promise<ApiResponse<ToolCallResponse>> {
    return this.post("/api/tools/call", { tool, args } as ToolCallRequest);
  }

  async initProject(projectName: string, path: string, language?: string, framework?: string): Promise<ApiResponse<ProjectInitResponse>> {
    return this.post("/api/project/init", { project_name: projectName, path, language, framework } as ProjectInitRequest);
  }
}

export const api = new ApiClient();
