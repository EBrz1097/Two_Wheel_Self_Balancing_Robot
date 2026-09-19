from pathlib import Path

import numpy as np


WEIGHTS_PATH = Path("exported_actor/actor_weights.npz")
OUTPUT_DIR = Path("exported_actor/c")


def c_float(value):
    """Generate a valid C float literal with float32 precision."""
    text = format(float(value), ".9g")

    if "." not in text and "e" not in text.lower():
        text += ".0"

    return text + "f"


def c_array(name, array):
    """Flatten arrays in row-major order."""
    values = np.asarray(array, dtype=np.float32).ravel(order="C")

    lines = []
    for start in range(0, len(values), 8):
        chunk = values[start:start + 8]
        lines.append(
            "    " + ", ".join(c_float(v) for v in chunk) + ","
        )

    return (
        f"static const float {name}[{len(values)}] = {{\n"
        + "\n".join(lines)
        + "\n};\n"
    )


def main():
    if not WEIGHTS_PATH.is_file():
        raise FileNotFoundError(WEIGHTS_PATH.resolve())

    expected_shapes = {
        "W1": (64, 2),
        "b1": (64,),
        "W2": (64, 64),
        "b2": (64,),
        "W3": (1, 64),
        "b3": (1,),
    }

    arrays = {}

    with np.load(WEIGHTS_PATH, allow_pickle=False) as data:
        for name, shape in expected_shapes.items():
            array = np.asarray(data[name], dtype=np.float32)

            if array.shape != shape:
                raise ValueError(
                    f"{name}: expected {shape}, got {array.shape}"
                )

            if not np.all(np.isfinite(array)):
                raise ValueError(f"{name} contains non-finite values")

            arrays[name] = array.copy()

        if not np.array_equal(
            data["action_low"],
            np.array([-25.0], dtype=np.float32),
        ):
            raise ValueError("Unexpected action_low")

        if not np.array_equal(
            data["action_high"],
            np.array([25.0], dtype=np.float32),
        ):
            raise ValueError("Unexpected action_high")

    header = """\
#ifndef SAC_ACTOR_H
#define SAC_ACTOR_H

#ifdef __cplusplus
extern "C" {
#endif

/*
 * Deterministic SAC inference.
 * obs0 and obs1 must match the original model observations.
 * Returns the model action in [-25, 25] for finite inputs.
 * No sensor preprocessing or PWM conversion is performed here.
 */
float sac_actor_predict(float obs0, float obs1);

#ifdef __cplusplus
}
#endif

#endif /* SAC_ACTOR_H */
"""

    source_parts = [
        '#include "sac_actor.h"\n',
        "#include <math.h>\n\n",
    ]

    for name, array in arrays.items():
        source_parts.append(c_array(name, array))
        source_parts.append("\n")

    source_parts.append("""\
float sac_actor_predict(float obs0, float obs1)
{
    float h1[64];
    float h2[64];
    float sum;
    float normalized_action;
    float action;
    int i;
    int j;

    /* Layer 1: Linear(2, 64) + ReLU */
    for (i = 0; i < 64; ++i)
    {
        sum = b1[i];
        sum += W1[i * 2] * obs0;
        sum += W1[i * 2 + 1] * obs1;

        h1[i] = (sum < 0.0f) ? 0.0f : sum;
    }

    /* Layer 2: Linear(64, 64) + ReLU */
    for (i = 0; i < 64; ++i)
    {
        sum = b2[i];

        for (j = 0; j < 64; ++j)
        {
            sum += W2[i * 64 + j] * h1[j];
        }

        h2[i] = (sum < 0.0f) ? 0.0f : sum;
    }

    /* Mean head: Linear(64, 1) */
    sum = b3[0];

    for (j = 0; j < 64; ++j)
    {
        sum += W3[j] * h2[j];
    }

    normalized_action = tanhf(sum);

    /* Match SB3 unscale_action for bounds [-25, 25]. */
    action = -25.0f
           + (0.5f * (normalized_action + 1.0f)) * 50.0f;

    return action;
}
""")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    header_path = OUTPUT_DIR / "sac_actor.h"
    source_path = OUTPUT_DIR / "sac_actor.c"

    header_path.write_text(header, encoding="utf-8")
    source_path.write_text("".join(source_parts), encoding="utf-8")

    parameter_count = sum(a.size for a in arrays.values())

    print("--- C export complete ---")
    print("Header:", header_path.resolve())
    print("Source:", source_path.resolve())
    print("Exported parameters:", parameter_count)
    print("Weight storage:", parameter_count * 4, "bytes")
    print("Local activation arrays:", 2 * 64 * 4, "bytes")
    print("Note: total stack usage must be checked on the target.")


if __name__ == "__main__":
    main()
