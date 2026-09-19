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
