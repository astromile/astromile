<template>
	<div class="result-item">
		<div class="result-item-label" v-bind:style="{width:wlabel}">{{label}}</div>
		<div class="result-item-value" v-bind:style="{width:wvalue}">{{computed ? value : '?'}}</div>
	</div>
</template>


<script>
export default {
	name: 'ResultItem',
	props: ['label','value','wlabel','wvalue', 'computed']
}
</script>

<style>
	.result-item-label {
		float: left;
	}
	.result-item-value {
		float:left;
	}
</style>