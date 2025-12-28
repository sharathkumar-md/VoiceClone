'use client';

import { InputHTMLAttributes, forwardRef, useState, useEffect } from 'react';

interface SliderProps extends Omit<InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label?: string;
  showValue?: boolean;
  unit?: string;
  formatValue?: (value: number) => string;
}

const Slider = forwardRef<HTMLInputElement, SliderProps>(
  ({ className = '', label, showValue = true, unit = '', formatValue, value, onChange, min = 0, max = 100, step = 1, ...props }, ref) => {
    const [currentValue, setCurrentValue] = useState(value || min);

    // Sync internal state when external value prop changes
    useEffect(() => {
      if (value !== undefined && value !== currentValue) {
        setCurrentValue(value);
      }
    }, [value]);

    const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
      setCurrentValue(e.target.value);
      onChange?.(e);
    };

    const displayValue = formatValue
      ? formatValue(Number(currentValue))
      : `${currentValue}${unit}`;

    return (
      <div className="w-full">
        {(label || showValue) && (
          <div className="flex justify-between items-center mb-2">
            {label && <label className="text-sm font-medium text-gray-700 dark:text-gray-300">{label}</label>}
            {showValue && <span className="text-sm font-mono text-gray-600 dark:text-gray-400">{displayValue}</span>}
          </div>
        )}
        <input
          ref={ref}
          type="range"
          className={`
            w-full h-2 bg-gray-200 dark:bg-gray-700 rounded-lg appearance-none cursor-pointer
            [&::-webkit-slider-thumb]:appearance-none
            [&::-webkit-slider-thumb]:w-4
            [&::-webkit-slider-thumb]:h-4
            [&::-webkit-slider-thumb]:rounded-full
            [&::-webkit-slider-thumb]:bg-blue-600
            [&::-webkit-slider-thumb]:cursor-pointer
            [&::-webkit-slider-thumb]:hover:bg-blue-700
            [&::-moz-range-thumb]:w-4
            [&::-moz-range-thumb]:h-4
            [&::-moz-range-thumb]:rounded-full
            [&::-moz-range-thumb]:bg-blue-600
            [&::-moz-range-thumb]:border-0
            [&::-moz-range-thumb]:cursor-pointer
            [&::-moz-range-thumb]:hover:bg-blue-700
            ${className}
          `}
          value={currentValue}
          onChange={handleChange}
          min={min}
          max={max}
          step={step}
          {...props}
        />
        <div className="flex justify-between text-xs text-gray-500 dark:text-gray-500 mt-1">
          <span>{min}{unit}</span>
          <span>{max}{unit}</span>
        </div>
      </div>
    );
  }
);

Slider.displayName = 'Slider';

export { Slider };
