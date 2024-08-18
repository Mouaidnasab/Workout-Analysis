import pandas as pd

# Load the cleaned data
df = pd.read_csv("angles_data.csv")

# Remove outliers where angle changes by more than 30 degrees between consecutive frames within the same video
def remove_frame_outliers(df, angle_columns, threshold=30):
    filtered_data = []
    for video_id in df['video_id'].unique():
        video_data = df[df['video_id'] == video_id].copy()
        valid_indices = video_data.index.tolist()
        
        for col in angle_columns:
            changes = video_data[col].diff().abs().fillna(0)
            valid_changes = changes <= threshold
            valid_indices = video_data[valid_changes].index.tolist()
            video_data = video_data.loc[valid_indices]
        
        filtered_data.append(video_data)
    
    return pd.concat(filtered_data, ignore_index=True)

angle_columns = ["right_elbow_angle", "right_shoulder_angle", "right_hip_angle", "right_knee_angle", "right_ankle_angle"]
df_cleaned = remove_frame_outliers(df, angle_columns)

# Filter angles based on given ranges
def filter_angles(df):
    conditions = (
        (df['right_shoulder_angle'].between(0, 110) | df['right_shoulder_angle'].between(320, 360)) &
        (df['right_hip_angle'].between(90, 190)) &
        (df['right_knee_angle'].between(0, 190)) &
        (df['right_elbow_angle'].between(0, 185)) &
        (df['right_ankle_angle'].between(80, 170))
    )
    return df[conditions]

df_filtered = filter_angles(df_cleaned)

# Extract correct and incorrect poses
correct_poses = df_filtered[df_filtered['label'] == 1]
incorrect_poses = df_filtered[df_filtered['label'] == 0]

# Calculate the min and max for each joint
def calculate_ranges(df, column):
    return df[column].min(), df[column].max()

def calculate_optimal_ranges(correct_range, incorrect_range):
    correct_min, correct_max = correct_range
    incorrect_min, incorrect_max = incorrect_range
    
    optimal_min = max(correct_min, incorrect_max)
    optimal_max = min(correct_max, incorrect_min)
    
    if optimal_min > optimal_max:
        optimal_min, optimal_max = correct_min, correct_max
        
    return optimal_min, optimal_max

joint_ranges = {}
for joint in angle_columns:
    if joint == "right_shoulder_angle":
        correct_range1 = calculate_ranges(correct_poses[correct_poses[joint] <= 110], joint)
        correct_range2 = calculate_ranges(correct_poses[correct_poses[joint] >= 310], joint)
        incorrect_range1 = calculate_ranges(incorrect_poses[incorrect_poses[joint] <= 110], joint)
        incorrect_range2 = calculate_ranges(incorrect_poses[incorrect_poses[joint] >= 310], joint)
        
        optimal_range1 = calculate_optimal_ranges(correct_range1, incorrect_range1)
        optimal_range2 = calculate_optimal_ranges(correct_range2, incorrect_range2)
        
        joint_ranges[joint] = {"optimal_range1": optimal_range1, "optimal_range2": optimal_range2}
    else:
        correct_range = calculate_ranges(correct_poses, joint)
        incorrect_range = calculate_ranges(incorrect_poses, joint)
        
        optimal_range = calculate_optimal_ranges(correct_range, incorrect_range)
        
        joint_ranges[joint] = {"optimal_range": optimal_range}

# Save the optimal ranges to a CSV file
ranges_data = []
for joint, ranges in joint_ranges.items():
    if joint == "right_shoulder_angle":
        ranges_data.append([
            joint,
            ranges["optimal_range1"][0], ranges["optimal_range1"][1],
            ranges["optimal_range2"][0], ranges["optimal_range2"][1]
        ])
    else:
        ranges_data.append([
            joint,
            ranges["optimal_range"][0], ranges["optimal_range"][1],
            None, None
        ])

ranges_df = pd.DataFrame(ranges_data, columns=[
    "joint",
    "optimal_min_range1", "optimal_max_range1",
    "optimal_min_range2", "optimal_max_range2"
])
ranges_df.to_csv("optimal_joint_angle_ranges.csv", index=False)
