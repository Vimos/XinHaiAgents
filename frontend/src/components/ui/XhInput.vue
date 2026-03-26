<template>
  <div :class="['xh-input-wrapper', { 'xh-input--focused': isFocused }]">
    <label v-if="label" class="xh-input__label">
      {{ label }}
      <span v-if="required" class="xh-input__required">*</span>
    </label>
    
    <div class="xh-input__container">
      <span v-if="prefix" class="xh-input__prefix">{{ prefix }}</span>
      
      <input
        ref="inputRef"
        :type="type"
        :value="modelValue"
        :placeholder="placeholder"
        :disabled="disabled"
        :readonly="readonly"
        :required="required"
        :maxlength="maxlength"
        @input="handleInput"
        @focus="handleFocus"
        @blur="handleBlur"
        @keydown="handleKeydown"
      />
      
      <span v-if="suffix" class="xh-input__suffix">{{ suffix }}</span>
      
      <!-- 清除按钮 -->
      <button
        v-if="clearable && modelValue"
        type="button"
        class="xh-input__clear"
        @click="clearInput"
      >
        ×
      </button>
    </div>
    
    <div v-if="error" class="xh-input__error">
      {{ error }}
    </div>
    
    <div v-else-if="hint" class="xh-input__hint">
      {{ hint }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  modelValue: String,
  type: {
    type: String,
    default: 'text'
  },
  label: String,
  placeholder: String,
  prefix: String,
  suffix: String,
  hint: String,
  error: String,
  disabled: Boolean,
  readonly: Boolean,
  required: Boolean,
  clearable: Boolean,
  maxlength: Number,
  autofocus: Boolean
})

const emit = defineEmits(['update:modelValue', 'focus', 'blur', 'keydown', 'clear'])

const inputRef = ref(null)
const isFocused = ref(false)

const handleInput = (e) => {
  emit('update:modelValue', e.target.value)
}

const handleFocus = (e) => {
  isFocused.value = true
  emit('focus', e)
}

const handleBlur = (e) => {
  isFocused.value = false
  emit('blur', e)
}

const handleKeydown = (e) => {
  emit('keydown', e)
  if (e.key === 'Enter') {
    emit('submit', e)
  }
}

const clearInput = () => {
  emit('update:modelValue', '')
  emit('clear')
  inputRef.value?.focus()
}

const focus = () => {
  inputRef.value?.focus()
}

defineExpose({
  focus,
  input: inputRef
})
</script>

<style scoped>
.xh-input-wrapper {
  display: flex;
  flex-direction: column;
  gap: var(--space-sm);
}

.xh-input__label {
  font-size: var(--text-sm);
  font-weight: 500;
  color: var(--text-secondary);
}

.xh-input__required {
  color: var(--accent-danger);
  margin-left: 2px;
}

.xh-input__container {
  position: relative;
  display: flex;
  align-items: center;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  transition: all var(--transition-fast);
  overflow: hidden;
}

.xh-input--focused .xh-input__container {
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(0, 212, 255, 0.15);
}

.xh-input__container input {
  flex: 1;
  padding: var(--space-sm) var(--space-md);
  background: transparent;
  border: none;
  color: var(--text-primary);
  font-size: var(--text-base);
  font-family: var(--font-family);
  outline: none;
}

.xh-input__container input::placeholder {
  color: var(--text-muted);
}

.xh-input__container input:disabled {
  cursor: not-allowed;
  opacity: 0.6;
}

.xh-input__prefix,
.xh-input__suffix {
  padding: 0 var(--space-sm);
  color: var(--text-secondary);
  font-size: var(--text-sm);
}

.xh-input__prefix {
  padding-left: var(--space-md);
  border-right: 1px solid var(--border-color);
  margin-right: var(--space-sm);
}

.xh-input__suffix {
  padding-right: var(--space-md);
  border-left: 1px solid var(--border-color);
  margin-left: var(--space-sm);
}

.xh-input__clear {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 20px;
  height: 20px;
  margin-right: var(--space-sm);
  padding: 0;
  background: var(--bg-tertiary);
  border: none;
  border-radius: var(--radius-full);
  color: var(--text-secondary);
  font-size: var(--text-sm);
  cursor: pointer;
  transition: all var(--transition-fast);
}

.xh-input__clear:hover {
  background: var(--accent-danger);
  color: white;
}

.xh-input__error {
  font-size: var(--text-sm);
  color: var(--accent-danger);
}

.xh-input__hint {
  font-size: var(--text-sm);
  color: var(--text-muted);
}
</style>
