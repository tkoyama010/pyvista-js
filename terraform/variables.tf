variable "github_token" {
  description = "GitHub personal access token with repo:admin scope"
  type        = string
  sensitive   = true
}

variable "github_owner" {
  description = "GitHub repository owner"
  type        = string
  default     = "tkoyama010"
}

variable "github_repository" {
  description = "GitHub repository name"
  type        = string
  default     = "pyvista-js"
}

variable "branch_name" {
  description = "Branch to protect"
  type        = string
  default     = "main"
}
