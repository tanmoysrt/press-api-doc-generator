<script setup>
import MarkdownIt from "markdown-it";
import MarkdownItAbbr from "markdown-it-abbr";
import MarkdownItAnchor from "markdown-it-anchor";
import MarkdownItFootnote from "markdown-it-footnote";

defineProps({
    source: {
        type: String,
        default: "",
    },
    isSmallText: {
        type: Boolean,
        default: false,
    },
});

const markdown = new MarkdownIt()
    .use(MarkdownItAbbr)
    .use(MarkdownItAnchor)
    .use(MarkdownItFootnote);

// force open links in new tab
const defaultRender =
    markdown.renderer.rules.link_open ||
    function (tokens, idx, options, env, self) {
        return self.renderToken(tokens, idx, options);
    };

markdown.renderer.rules.link_open = function (tokens, idx, options, env, self) {
    tokens[idx].attrSet("target", "_blank");
    return defaultRender(tokens, idx, options, env, self);
};
</script>

<template>
    <div
        class="prose max-w-full"
        :class="{
            'prose-sm font-normal': isSmallText,
        }"
        v-html="markdown.render(source)"
    />
</template>
