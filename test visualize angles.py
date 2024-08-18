import pygame
import math

# Initialize Pygame
pygame.init()

# Set up display
width, height = 800, 600
window = pygame.display.set_mode((width, height))
pygame.display.set_caption('2D Character Angle Visualization')

# Define colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# Define points
points = {
    "shoulder": [400, 200],
    "elbow": [450, 300],
    "wrist": [500, 400],
    "hip": [400, 400],
    "knee": [450, 500],
    "ankle": [500, 600]
}

# Define function to calculate angle
def calculate_angle(p1, p2, p3):
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    angle = math.degrees(math.atan2(y3 - y2, x3 - x2) - math.atan2(y1 - y2, x1 - x2))
    if angle < 0:
        angle += 360
    return angle

# Run the game loop
running = True
selected_point = None

while running:
    window.fill(white)
    
    # Draw lines and points
    pygame.draw.line(window, black, points["shoulder"], points["elbow"], 2)
    pygame.draw.line(window, black, points["elbow"], points["wrist"], 2)
    pygame.draw.line(window, black, points["shoulder"], points["hip"], 2)
    pygame.draw.line(window, black, points["hip"], points["knee"], 2)
    pygame.draw.line(window, black, points["knee"], points["ankle"], 2)
    
    for point in points:
        pygame.draw.circle(window, red, points[point], 5)
    
    # Calculate and display angles
    elbow_angle = calculate_angle(points["shoulder"], points["elbow"], points["wrist"])
    shoulder_angle = calculate_angle(points["elbow"], points["shoulder"], points["hip"])
    hip_angle = calculate_angle(points["knee"], points["hip"], points["shoulder"])
    knee_angle = calculate_angle(points["hip"], points["knee"], points["ankle"])

    font = pygame.font.Font(None, 36)
    angles_text = [
        f'Elbow: {elbow_angle:.2f}',
        f'Shoulder: {shoulder_angle:.2f}',
        f'Hip: {hip_angle:.2f}',
        f'Knee: {knee_angle:.2f}',
    ]

    for i, text in enumerate(angles_text):
        angle_surface = font.render(text, True, black)
        window.blit(angle_surface, (10, 10 + i * 30))
    
    pygame.display.flip()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        elif event.type == pygame.MOUSEBUTTONDOWN:
            for point in points:
                if math.hypot(points[point][0] - event.pos[0], points[point][1] - event.pos[1]) < 10:
                    selected_point = point
                    break
        
        elif event.type == pygame.MOUSEBUTTONUP:
            selected_point = None
        
        elif event.type == pygame.MOUSEMOTION and selected_point:
            points[selected_point] = list(event.pos)

pygame.quit()
