using UnityEngine;
using Unity.MLAgents;
using Unity.MLAgents.Actuators;
using Unity.MLAgentsExamples;
using Unity.MLAgents.Sensors;
using Random = UnityEngine.Random;

namespace SpiderGame.SpiderAgent
{
    /// <summary>
    /// Spider Agent that learns to walk using ML-Agents
    /// </summary>
    /// <remarks>
    /// The agent learns to:
    /// - Match a target walking speed
    /// - Face the direction it's moving
    /// - Maintain upright orientation
    /// - Navigate towards targets
    /// </remarks>
    [RequireComponent(typeof(JointDriveController))]
    public class SpiderAgent : Agent
    {
        [Header("Reward Settings")]
        [SerializeField]
        [Tooltip("Episode will end if accumulated reward falls below this threshold")]
        private float minRewardThreshold = -100f;

        [Header("Walk Speed")]
        [Range(0.1f, m_maxWalkingSpeed)]
        [SerializeField]
        [Tooltip("The speed the agent will try to match")]
        private float m_TargetWalkingSpeed = m_maxWalkingSpeed;

        const float m_maxWalkingSpeed = 20;

        public float TargetWalkingSpeed
        {
            get { return m_TargetWalkingSpeed; }
            set { m_TargetWalkingSpeed = Mathf.Clamp(value, .1f, m_maxWalkingSpeed); }
        }

        void Start()
        {
            // Validate speeds
            m_TargetWalkingSpeed = Mathf.Clamp(m_TargetWalkingSpeed, 0.1f, m_maxWalkingSpeed);
        }

        //The direction an agent will walk during training.
        [Header("Target To Walk Towards")]
        public Transform TargetPrefab; //Target prefab to use in Dynamic envs
        private Transform m_Target; //Target the agent will walk towards during training.

        [Header("Body Parts")][Space(10)] public Transform body;
        public Transform leg0Upper;
        public Transform leg0Lower;
        public Transform leg1Upper;
        public Transform leg1Lower;
        public Transform leg2Upper;
        public Transform leg2Lower;
        public Transform leg3Upper;
        public Transform leg3Lower;

        //This will be used as a stabilized model space reference point for observations
        //Because ragdolls can move erratically during training, using a stabilized reference transform improves learning
        OrientationCubeController m_OrientationCube;

        //The indicator graphic gameobject that points towards the target
        DirectionIndicator m_DirectionIndicator;
        JointDriveController m_JdController;

        public override void Initialize()
        {
            // Initialize target speed before anything else
            m_TargetWalkingSpeed = m_maxWalkingSpeed;

            SpawnTarget(TargetPrefab, transform.position); //spawn target

            m_OrientationCube = GetComponentInChildren<OrientationCubeController>();
            m_DirectionIndicator = GetComponentInChildren<DirectionIndicator>();
            m_JdController = GetComponent<JointDriveController>();

            //Setup each body part
            m_JdController.SetupBodyPart(body);
            m_JdController.SetupBodyPart(leg0Upper);
            m_JdController.SetupBodyPart(leg0Lower);
            m_JdController.SetupBodyPart(leg1Upper);
            m_JdController.SetupBodyPart(leg1Lower);
            m_JdController.SetupBodyPart(leg2Upper);
            m_JdController.SetupBodyPart(leg2Lower);
            m_JdController.SetupBodyPart(leg3Upper);
            m_JdController.SetupBodyPart(leg3Lower);
        }

        /// <summary>
        /// Spawns a target prefab at pos
        /// </summary>
        /// <param name="prefab"></param>
        /// <param name="pos"></param>
        void SpawnTarget(Transform prefab, Vector3 pos)
        {
            m_Target = Instantiate(prefab, pos, Quaternion.identity, transform.parent);
        }

        /// <summary>
        /// Loop over body parts and reset them to initial conditions.
        /// </summary>
        public override void OnEpisodeBegin()
        {
            foreach (var bodyPart in m_JdController.bodyPartsDict.Values)
            {
                bodyPart.Reset(bodyPart);
            }

            //Random start rotation to help generalize
            body.rotation = Quaternion.Euler(0, Random.Range(0.0f, 360.0f), 0);

            UpdateOrientationObjects();
        }

        /// <summary>
        /// Add relevant information on each body part to observations.
        /// </summary>
        public void CollectObservationBodyPart(BodyPart bp, VectorSensor sensor)
        {
            //GROUND CHECK
            sensor.AddObservation(bp.groundContact.touchingGround); // Is this bp touching the ground

            if (bp.rb.transform != body)
            {
                sensor.AddObservation(bp.currentStrength / m_JdController.maxJointForceLimit);
            }
        }

        /// <summary>
        /// Loop over body parts to add them to observation.
        /// </summary>
        public override void CollectObservations(VectorSensor sensor)
        {
            var cubeForward = m_OrientationCube.transform.forward;

            // Add normalized target speed to observations
            sensor.AddObservation(TargetWalkingSpeed / m_maxWalkingSpeed);

            //velocity we want to match
            var velGoal = cubeForward * TargetWalkingSpeed;
            //ragdoll's avg vel
            var avgVel = GetAvgVelocity();

            //current ragdoll velocity. normalized
            sensor.AddObservation(Vector3.Distance(velGoal, avgVel));
            //avg body vel relative to cube
            sensor.AddObservation(m_OrientationCube.transform.InverseTransformDirection(avgVel));
            //vel goal relative to cube
            sensor.AddObservation(m_OrientationCube.transform.InverseTransformDirection(velGoal));
            //rotation delta
            sensor.AddObservation(Quaternion.FromToRotation(body.forward, cubeForward));

            //Add pos of target relative to orientation cube
            sensor.AddObservation(m_OrientationCube.transform.InverseTransformPoint(m_Target.transform.position));

            RaycastHit hit;
            float maxRaycastDist = 10;
            if (Physics.Raycast(body.position, Vector3.down, out hit, maxRaycastDist))
            {
                sensor.AddObservation(hit.distance / maxRaycastDist);
            }
            else
                sensor.AddObservation(1);

            foreach (var bodyPart in m_JdController.bodyPartsList)
            {
                CollectObservationBodyPart(bodyPart, sensor);
            }
        }

        public override void OnActionReceived(ActionBuffers actionBuffers)
        {
            // The dictionary with all the body parts in it are in the jdController
            var bpDict = m_JdController.bodyPartsDict;

            var continuousActions = actionBuffers.ContinuousActions;
            var i = -1;
            // Pick a new target joint rotation
            bpDict[leg0Upper].SetJointTargetRotation(continuousActions[++i], continuousActions[++i], 0);
            bpDict[leg1Upper].SetJointTargetRotation(continuousActions[++i], continuousActions[++i], 0);
            bpDict[leg2Upper].SetJointTargetRotation(continuousActions[++i], continuousActions[++i], 0);
            bpDict[leg3Upper].SetJointTargetRotation(continuousActions[++i], continuousActions[++i], 0);
            bpDict[leg0Lower].SetJointTargetRotation(continuousActions[++i], 0, 0);
            bpDict[leg1Lower].SetJointTargetRotation(continuousActions[++i], 0, 0);
            bpDict[leg2Lower].SetJointTargetRotation(continuousActions[++i], 0, 0);
            bpDict[leg3Lower].SetJointTargetRotation(continuousActions[++i], 0, 0);

            // Update joint strength
            bpDict[leg0Upper].SetJointStrength(continuousActions[++i]);
            bpDict[leg1Upper].SetJointStrength(continuousActions[++i]);
            bpDict[leg2Upper].SetJointStrength(continuousActions[++i]);
            bpDict[leg3Upper].SetJointStrength(continuousActions[++i]);
            bpDict[leg0Lower].SetJointStrength(continuousActions[++i]);
            bpDict[leg1Lower].SetJointStrength(continuousActions[++i]);
            bpDict[leg2Lower].SetJointStrength(continuousActions[++i]);
            bpDict[leg3Lower].SetJointStrength(continuousActions[++i]);
        }

        /// <summary>
        /// Calculates the combined reward for movement and orientation
        /// </summary>
        private float CalculateReward()
        {
            var cubeForward = m_OrientationCube.transform.forward;

            // a. Match target speed
            var matchSpeedReward = GetMatchingVelocityReward(cubeForward * TargetWalkingSpeed, GetAvgVelocity());

            // b. Rotation alignment with target direction.
            var lookAtTargetReward = (Vector3.Dot(cubeForward, body.forward) + 1) * .5F;

            float finalReward = matchSpeedReward * lookAtTargetReward;

            // Combine rewards
            return finalReward;
        }

        void FixedUpdate()
        {
            UpdateOrientationObjects();
            AddReward(CalculateReward());

            if (GetCumulativeReward() <= minRewardThreshold)
            {
                EndEpisode();
            }
        }

        /// <summary>
        /// Normalized value of the difference in actual speed vs goal walking speed.
        /// </summary>
        public float GetMatchingVelocityReward(Vector3 velocityGoal, Vector3 actualVelocity)
        {
            //distance between our actual velocity and goal velocity
            var velDeltaMagnitude = Mathf.Clamp(Vector3.Distance(actualVelocity, velocityGoal), 0, TargetWalkingSpeed);

            //return the value on a declining sigmoid shaped curve that decays from 1 to 0
            //This reward will approach 1 if it matches perfectly and approach zero as it deviates
            return Mathf.Pow(1 - Mathf.Pow(velDeltaMagnitude / TargetWalkingSpeed, 2), 2);
        }

        /// <summary>
        /// Update OrientationCube and DirectionIndicator
        /// </summary>
        void UpdateOrientationObjects()
        {
            m_OrientationCube.UpdateOrientation(body, m_Target);
            if (m_DirectionIndicator)
            {
                m_DirectionIndicator.MatchOrientation(m_OrientationCube.transform);
            }
        }

        /// <summary>
        ///Returns the average velocity of all of the body parts
        ///Using the velocity of the body only has shown to result in more erratic movement from the limbs
        ///Using the average helps prevent this erratic movement
        /// </summary>
        Vector3 GetAvgVelocity()
        {
            Vector3 velSum = Vector3.zero;
            Vector3 avgVel = Vector3.zero;

            //ALL RBS
            int numOfRb = 0;
            foreach (var item in m_JdController.bodyPartsList)
            {
                numOfRb++;
                velSum += item.rb.linearVelocity;
            }

            avgVel = velSum / numOfRb;
            return avgVel;
        }

        /// <summary>
        /// Agent touched the target
        /// </summary>
        public void TouchedTarget()
        {
            AddReward(1f);
        }
    }

}