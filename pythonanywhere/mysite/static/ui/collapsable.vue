<template>
	<div>
		<div :class="{title_collapsed:isCollapsed, title_uncollapsed:!isCollapsed}"
		     @click="onPMClicked">
			<p>{{openclose}} {{label}} <hr></p>
		</div>
		<div :class="{collapsed:isCollapsed, uncollapsed:!isCollapsed}">
			<slot></slot>
			<hr>
		</div>
	</div>
</template>

<script>
export default {
	name: 'Collapsable',
	props: {
		label: { type: String },
		collapsed: { type: Boolean }
	},
	data: function() {
		return {
			isCollapsed: this.collapsed,
		}
	},
	computed: {
		openclose: function() {
			return this.isCollapsed ? 'v' : '^'
		}
	},
	methods: {
		onPMClicked: function() {
			//console.log('+/- clicked')
			this.isCollapsed = !this.isCollapsed
		},
	}
}

</script>

<style>
.title_collapsed {
	background: #aba;
	font-weight: bold;
}

.title_uncollapsed {
	background: #ddd;
	font-style: italic;
}

.collapsed {
	display: none;
}

.uncollapsed {
	display: block;
}
</style>