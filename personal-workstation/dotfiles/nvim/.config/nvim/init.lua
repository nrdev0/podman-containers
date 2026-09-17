vim.g.base46_cache = vim.fn.stdpath "data" .. "/base46/"
vim.g.mapleader = " "

-- bootstrap lazy and all plugins
local lazypath = vim.fn.stdpath "data" .. "/lazy/lazy.nvim"

if not vim.uv.fs_stat(lazypath) then
  local repo = "https://github.com/folke/lazy.nvim.git"
  vim.fn.system { "git", "clone", "--filter=blob:none", repo, "--branch=stable", lazypath }
  if vim.v.shell_error ~= 0 then
    error "Failed to clone lazy.nvim"
  end
  local lock = vim.json.decode(table.concat(vim.fn.readfile(vim.fn.stdpath "config" .. "/lazy-lock.json"), "\n"))
  vim.fn.system { "git", "-C", lazypath, "checkout", lock["lazy.nvim"].commit }
  if vim.v.shell_error ~= 0 then
    error "Failed to check out the locked lazy.nvim version"
  end
end

vim.opt.rtp:prepend(lazypath)

local lazy_config = require "configs.lazy"

-- load plugins
require("lazy").setup({
  {
    "NvChad/NvChad",
    lazy = false,
    branch = "v2.5",
    import = "nvchad.plugins",
  },

  { import = "plugins" },
}, lazy_config)

-- load theme
dofile(vim.g.base46_cache .. "defaults")
dofile(vim.g.base46_cache .. "statusline")

require "options"
require "autocmds"

vim.schedule(function()
  require "mappings"
end)
