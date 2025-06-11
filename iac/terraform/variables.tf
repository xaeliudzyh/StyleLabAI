# получаем из GitHub Secrets
variable "yc_token"   { type = string }
variable "cloud_id"   { type = string }
variable "folder_id"  { type = string }

# прочие параметры
variable "zone"    { type = string default = "ru-central1-a" }
variable "registry" { type = string }   # ID CR: crp1tis4c8hchmo7qb07
