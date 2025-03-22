import { API_IP, PORT } from "../constants";

const serverDomainUrl = `http://${API_IP}:${PORT}`;

// Helper functions
const handleResponse = async (response: Response) => {
  if (response.ok) return response.json();

  // Status not ok
  try {
    const data = await response.json();
    return Promise.reject(data || response.status);
  } catch {
    // Could not parse the JSON
    return Promise.reject(response.status);
  }
};

const useFetch = () => {
  const get = async (url: string) => {
    const requestOptions: RequestInit = {
      method: "GET",
    };
    const response = await fetch(serverDomainUrl + url, requestOptions);
    return handleResponse(response);
  };

  const post = async (url: string, body: any) => {
    const requestOptions: RequestInit = {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    };
    const response = await fetch(serverDomainUrl + url, requestOptions);
    return handleResponse(response);
  };

  const put = async (url: string, body: any) => {
    const requestOptions: RequestInit = {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    };
    const response = await fetch(serverDomainUrl + url, requestOptions);
    return handleResponse(response);
  };

  // prefixed with "_" since "delete" is a reserved word in javascript
  const _delete = async (url: string) => {
    const requestOptions: RequestInit = {
      method: "DELETE",
    };
    const response = await fetch(serverDomainUrl + url, requestOptions);
    return handleResponse(response);
  };

  return { get, post, put, _delete };
};

export default useFetch;
