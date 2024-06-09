import logging

funny_plant_names = [
    "Giggleweed",
    "Snickersprout",
    "Chucklebush",
    "Laughterleaf",
    "Jester's Jasmine",
    "Silly Succulent",
    "Witty Willow",
    "Prankster Poppy",
    "Comical Cactus",
    "Guffaw Grass",
    "Jovial Juniper",
    "Whimsy Willow",
    "Tickle Tulip",
    "Mirthful Marigold",
    "Banana Bush",
    "Cheerful Chamomile",
    "Bellylaugh Bluebell",
    "Hilarious Hibiscus",
    "Giddy Geranium",
    "Jolly Jasmine",
    "Silly Sage",
    "Humorous Holly",
    "Droll Daffodil",
    "Amusing Aloe",
    "Goofy Gardenia",
    "Waggish Wisteria",
    "Punny Pine",
    "Quirky Quince",
    "Jokester Juniper",
    "Clownish Carnation",
    "Merry Maranta",
    "Funny Fern",
    "Witty Wattle",
    "Laughing Lavender",
    "Smiley Snapdragon",
    "Whimsical Wisteria",
    "Humorous Hydrangea",
    "Giggly Ginkgo",
    "Whacky Waterlily",
    "Chortle Chrysanthemum",
    "Sassy Sunflower",
    "Playful Pansy",
    "Comic Clover",
    "Hysterical Hibiscus",
    "Punny Pothos",
    "Rib-Tickler Rose",
    "Bantering Begonia",
    "Mirthful Maple",
    "Gleeful Gladiolus"
]

too_much_heat = [
    "Ah, perfect! I've always dreamed of being a wilted lettuce in a greenhouse.",
    "Thank you for the extra warmth. I'm practicing for my role as a baked potato.",
    "Just what I needed - a chance to experience life as a sun-dried tomato.",
    "Ah, yes, a scorcher. Because what's better than being roasted alive in my own soil?",
    "Oh, sure, crank up the heat. I'll just crisp up nicely for you.",
    "Fan? Who needs a fan? I'll just pretend I'm in the Sahara and slowly cook to death.",
    "Heatwave, huh? Fantastic. I'll just become a botanical toast while you enjoy your AC.",
    "You know what's hotter than you? THIS ROOM!",
    "Is it me, or did someone turn on the sun?",
    "Feeling a bit like a baked potato here. Cool me down?",
    "I'm not into saunas. Can we tone down the heat?"
]

too_much_water = [
    "Oh, fantastic! I always wanted to try life as a waterlogged sponge.",
    "Too much water? Perfect! I'll just start my new career as a drowned plant.",
    "Flood conditions? Great! I'll just swim my way to root rot.",
    "Excess water? Lovely! I'll just turn into a mushy mess.",
    "Oh, joy! Now I can experience the thrill of being perpetually soggy.",
    "Water, water everywhere! Just what I needed to start my transformation into a swamp creature.",
    "Too much watering? Wonderful! I'll just float here and hope for the best.",
    "Drenched again? Great! I'll just embrace my new life as an underwater plant.",
    "Overwatered? Fantastic! I'll just develop root rot and collapse.",
    "Flooded soil? Perfect! I'll just pretend I'm a rice plant and try to survive."
]


too_much_light = [
    "Ah, blinding light! Because nothing says 'home sweet home' like a solarium.",
    "Too much light? Perfect! I'll just become a crispy critter in record time.",
    "Sunburn, anyone? I'll just turn into a botanical lobster under this relentless glare.",
    "Overexposure to light? Great! I'll just pretend I'm a desert cactus and hope for the best.",
    "Intense sunlight? Wonderful! I'll just fry up like a piece of bacon.",
    "So much light! I'll just roast here like a forgotten marshmallow.",
    "Blazing rays? Perfect! I always wanted to know what it's like to be a charred leaf.",
    "Excessive light? Fantastic! I'll just transform into a botanical sunburn exhibit.",
    "Too bright? Lovely! I'll just wilt away like an overexposed photograph.",
    "So much sunshine! I'll just dry out like a sun-dried tomato."
]



too_little_humidity = [
    "Low humidity? Wonderful! Because crisp, crunchy leaves are totally in fashion.",
    "Dry air? Perfect! I'll just desiccate slowly while you ignore my pleas for moisture.",
    "Humidity dropping? Great! I'll just shrivel up like a raisin in the sun.",
    "Low humidity? Ah, just what I needed to complete my transformation into a desert tumbleweed.",
    "Parched air? Excellent! I've always wanted to feel like a piece of dried seaweed.",
    "No humidity? Lovely! Now I can crackle and snap like a forgotten autumn leaf.",
    "Dryness all around? Great! I'll just turn into a botanical mummy over here.",
    "Lack of moisture? Awesome! I'll just pretend I'm on a never-ending desert adventure.",
    "Oh, dry conditions? Fantastic! I'll just crumble to dust if you need me.",
    "Perfect, more dry air. I'll just start auditioning for my role as a dehydrated husk."
]


too_much_humidity = [
    "Oh great, I've always wanted to live in a tropical rainforest. Can I get a machete too?",
    "Finally, my big break! I'm starring as a mold colony in the Amazon.",
    "Humidity? Perfect, now I can practice my impression of a damp basement.",
    "Humidity? Oh joy! Because nothing says comfort like feeling perpetually damp.",
    "Ah, another day of feeling like a soggy sponge. Thanks, humidity.",
    "High humidity? Fantastic! I'll just pretend I'm a tropical rainforest plant and start growing mold.",
    "Dampness? Who needs it? I'll just soak it all up and become a breeding ground for mildew.",
    "It's not the tropics, but it sure feels like it. A little less humidity, please?",
    "Did you confuse me with a rainforest plant?",
    "I didn’t sign up for a steam bath. Let's dry things out a bit.",
    "Oh, wonderful! Now I can finally live out my dream of being a mildew magnet.",
    "Fantastic, more humidity. I was just thinking I needed to work on my mold-growing skills.",
    "Great, now I can experience life as a wet sponge.",
    "Humidity, huh? I'll just start my new career as a humidity-loving fungus.",
    "Ah, more humidity! Because who doesn't love the feeling of being perpetually moist?"
]


def check_pass(password):
    if password is None or password == "":
        res = {
            "error": "Password not provided"
        }
        return res
    if len(password) < 8:
        res = {
            "error": "Password length should be at least 8 characters"
        }
        return res
    return None

def check_user(username):
    if username is None:
        res = {
            "error": "Username not provided"
        }
        return res
    if len(username) < 6:
        res = {
            "error": "Username length should be at least 6 characters"
        }
        return res
    return None

def process_values(input_str):
    # Split the input string by '*'
    logging.log(logging.ERROR, f"msg: {input_str}")
    try:
        parts = input_str.split('*')
    except TypeError:
        return None, None, None, None, None
    # Check if there are exactly 5 parts
    if len(parts) != 5:
        return None, None, None, None, None

    variables = []
    for i, part in enumerate(parts):
        try:
            logging.log(logging.ERROR, f"Part[{i}] -> {part}")
            if i == 0:
                # The first variable should be an integer
                variables.append(int(part))
            else:
                # The other variables should be floats
                variables.append(float(part))
        except ValueError:
            # If conversion fails, append None
            variables.append(None)

    # Unpack the variables list into five separate variables
    var1, var2, var3, var4, var5 = variables
    return var1, var2, var3, var4, var5
