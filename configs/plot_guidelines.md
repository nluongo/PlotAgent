# Plot Evaluation Guidelines

## Agent Behavior Rules

- **Max retries per plot**: Apply overrides and rerun at most **3 times** for any single plot. 
   If it still fails after 3 attempts, skip it and flag it in the summary.

## Axis Fit

1. **X-axis lower bound**: The leftmost filled bin must not touch the y-axis.
   Visible empty space before the first non-zero bin is required.
   A distribution beginning at the very left edge suggests `x_min` is too high
   (or not set, defaulting to a value that clips the distribution).

2. **X-axis upper bound**: The rightmost filled bin must not touch the right axis edge.
   A distribution ending abruptly at the right edge with a non-zero bin suggests
   `x_max` is too low.

3. **Y-axis upper bound**: The tallest stack element must not touch or exceed the
   y-axis maximum. Clear whitespace above the highest point is required (linear and log).

4. **Y-axis lower bound (log scale)**: On log scale, the lowest bars must not be
   truncated at the bottom. If they appear cut off, `y_min` may be too high.

## Overflow / Underflow

- If there is a visible spike at the leftmost or rightmost bin significantly taller
  than its neighbours, it likely collects overflow/underflow entries. Widen the axis
  range to absorb them.

## Legend and Labels

- The legend must not overlap any filled histogram bar or the ATLAS label block.
- All axis tick labels must be fully visible (not clipped by the canvas edge).

## Ratio Panel (when present)

- The ratio panel y-axis should span a symmetric range around 1.0 (e.g. 0.5–1.5).
  If data points fall outside this range the ratio `y_min`/`y_max` may need widening.
- The ratio panel must show a visible unity line at y = 1.

## Signal Overlay (when present)

- Signal curves must be distinguishable from the background stack (different colour/style).
- Signal curves must not be completely hidden below the background.

## Applying Fixes

Use `apply_plot_override` with the exact `histogram` and `selection` keys matching the
plot filename stem (format: `{histogram}_{selection}`). Supported override keys:

| Key | Type | Effect |
|-----|------|--------|
| `x_min` | float | Left edge of x-axis |
| `x_max` | float | Right edge of x-axis |
| `nBins` | int | Number of bins (changes bin width) |
| `log_scale` | bool | Enable log y-axis |
