# frozen_string_literal: true

source "https://rubygems.org"

ruby ">= 3.1", "< 4.0"

gem "jekyll-theme-chirpy", "~> 7.5"

group :test do
  gem "debug", "~> 1.11"
  gem "html-proofer", "~> 5.0"
end

platforms :windows, :jruby do
  gem "tzinfo", ">= 1", "< 3"
  gem "tzinfo-data"
end

gem "wdm", "~> 0.2.0", platforms: [:windows]
