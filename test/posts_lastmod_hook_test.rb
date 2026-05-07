# frozen_string_literal: true

require "minitest/autorun"
require "open3"
require "ostruct"

module Jekyll
  module Hooks
    class << self
      attr_reader :registered_hook

      def register(collection, event, &block)
        @registered_hook = [collection, event, block]
      end
    end
  end
end

class PostsLastmodHookTest < Minitest::Test
  def setup
    @calls = []
  end

  def test_git_commands_are_called_without_shell_interpolation
    require_relative "../_plugins/posts-lastmod-hook"

    post = OpenStruct.new(
      path: '_posts/2026-05-01-title"; touch /tmp/unsafe.md',
      data: {}
    )

    Open3.stub(:capture2, lambda { |*args|
      @calls << args
      args.include?("--pretty=%ad") ? ["2026-05-07 12:00:00 +0900\n", double_success] : ["2\n", double_success]
    }) do
      Jekyll::Hooks.registered_hook[2].call(post)
    end

    assert_equal "2026-05-07 12:00:00 +0900", post.data["last_modified_at"]
    assert_equal ["git", "rev-list", "--count", "HEAD", "--", post.path], @calls.first
    assert_equal ["git", "log", "-1", "--pretty=%ad", "--date=iso", "--", post.path], @calls.last
  end

  private

  def double_success
    OpenStruct.new(success?: true)
  end
end
