variable "zone" {
  type    = string
  default = "ru-central1-a"
}

variable "yc_token"   { type = string }
variable "cloud_id"   { type = string }
variable "folder_id"  { type = string }

variable "registry" {
  type = string
}

variable "iam_sa_id" {
  type = string
}

variable "node_sa_id" {
  type = string
}

