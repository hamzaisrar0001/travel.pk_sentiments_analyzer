"""
generate_dataset.py
───────────────────
Generates reviews_dataset.csv with 125 labeled hotel/travel reviews for Pakistan.
Run once:  python data/generate_dataset.py
"""

import csv
import os

REVIEWS = [
    # ── POSITIVE (id 1-50) ───────────────────────────────────────────────────
    (1,  "Pearl Continental Lahore exceeded all our expectations. The room was spotless, staff incredibly helpful and the rooftop restaurant served outstanding continental cuisine.",
     "positive", "Cleanliness,Staff,Food", "train", "Pearl Continental Lahore"),

    (2,  "Serena Hotel Islamabad is the epitome of luxury. Perfect location near the diplomatic enclave, rooms are beautifully maintained, and the breakfast buffet is exceptional.",
     "positive", "Location,Cleanliness,Food", "train", "Serena Hotel Islamabad"),

    (3,  "Stayed at Marriott Karachi for a business trip. Service was impeccable, the conference facilities top-notch, and the seaview room was breathtaking. Worth every rupee.",
     "positive", "Staff,Location,Value for Money", "train", "Marriott Karachi"),

    (4,  "The guesthouses in Hunza are something else! Incredibly clean, hosts very warm and welcoming, and the local food – apricot dishes and chapshuro – absolutely delicious.",
     "positive", "Cleanliness,Staff,Food", "train", "Hunza Valley Guesthouse"),

    (5,  "Avari Towers Lahore is ideally located in the heart of the city. The breakfast buffet is legendary, and rooms are always well-maintained. Consistent quality every time.",
     "positive", "Location,Food,Cleanliness", "train", "Avari Towers Lahore"),

    (6,  "Our stay at Swat Serena was magical. Rooms had stunning valley views, staff was attentive, and the food was a perfect blend of local and continental dishes.",
     "positive", "Location,Staff,Food", "train", "Serena Hotel Swat"),

    (7,  "Budget guesthouse in Murree but immaculately clean. The caretaker was extremely helpful, provided hot water on demand, and the location near Mall Road is very convenient.",
     "positive", "Cleanliness,Staff,Location", "train", "Murree Guesthouse"),

    (8,  "The Islamabad Serena's staff remembered our names from our previous visit. That personal touch combined with spotless rooms and excellent food makes it our go-to hotel.",
     "positive", "Staff,Cleanliness,Food", "train", "Serena Hotel Islamabad"),

    (9,  "Gilgit Serena's location by the river is unbeatable. Staff goes above and beyond to help with local sightseeing. The dal and fresh bread was utterly delicious.",
     "positive", "Location,Staff,Food", "train", "Serena Hotel Gilgit"),

    (10, "Pearl Continental Karachi delivers consistent excellence. Clean rooms, professional staff, delicious seafood at the restaurant, and great value for a 5-star property.",
     "positive", "Cleanliness,Staff,Food,Value for Money", "train", "Pearl Continental Karachi"),

    (11, "The Rose Hotel Lahore offers great value for money. Rooms are clean and comfortable, location is central, and staff is polite and responsive to all our requests.",
     "positive", "Value for Money,Cleanliness,Location,Staff", "train", "Rose Hotel Lahore"),

    (12, "Stayed at Mövenpick Karachi for our anniversary. The sea-facing room was gorgeous, staff arranged a surprise decoration, and the dinner was absolutely phenomenal.",
     "positive", "Location,Staff,Food", "train", "Mövenpick Karachi"),

    (13, "Fairy Meadows camping experience was spectacular. The campsite was maintained well, guides were expert, and the mountain views were worth every bit of difficulty.",
     "positive", "Location,Cleanliness,Staff", "train", "Fairy Meadows Camp"),

    (14, "PC Bhurban is a gem in the mountains. Rooms are luxurious and clean, food at the main restaurant is superb, and the pine-forest surroundings are incredibly peaceful.",
     "positive", "Cleanliness,Food,Location", "train", "Pearl Continental Bhurban"),

    (15, "Hotel One Multan surprised me with its cleanliness and modern amenities. Staff were friendly, breakfast was good, and the price point is truly excellent.",
     "positive", "Cleanliness,Staff,Food,Value for Money", "train", "Hotel One Multan"),

    (16, "The staff at Lalazar Hotel in Naran were heroes during our trip – they helped with flooded roads, provided extra blankets, and kept the place warm and clean throughout.",
     "positive", "Staff,Cleanliness", "train", "Lalazar Hotel Naran"),

    (17, "Ramada Lahore is conveniently located near the airport. Rooms are spacious and clean, staff handles late check-ins graciously, and the buffet is well worth it.",
     "positive", "Location,Cleanliness,Staff,Food", "train", "Ramada Lahore"),

    (18, "The Lal Qila Hotel in Rawalpindi provides amazing value. Clean rooms, helpful reception staff, and a location that is great for exploring the twin cities.",
     "positive", "Value for Money,Cleanliness,Staff,Location", "train", "Lal Qila Hotel Rawalpindi"),

    (19, "Best breakfast I have had at any hotel in Pakistan – at PC Lahore! Eggs made to order, fresh juices, and amazing pastries. The room was immaculate as well.",
     "positive", "Food,Cleanliness", "train", "Pearl Continental Lahore"),

    (20, "Hotel Shelton Islamabad has a superb location near Blue Area. Staff are professional, rooms are neat and clean, and prices are reasonable for the quality.",
     "positive", "Location,Staff,Cleanliness,Value for Money", "train", "Hotel Shelton Islamabad"),

    (21, "Our family trip to Skardu was made perfect by the guesthouse – clean rooms, delicious home-cooked food, and a host who treated us like family.",
     "positive", "Cleanliness,Food,Staff", "train", "Skardu Guesthouse"),

    (22, "The Four Seasons apartments in Islamabad are spotlessly clean. The kitchen is fully equipped, location is great, and the management is highly responsive.",
     "positive", "Cleanliness,Location,Staff", "train", "Four Seasons Apartments Islamabad"),

    (23, "Best hotel experience in Faisalabad at Hotel Crown. The food was superb – try the halwa puri breakfast! Staff was attentive and rooms well-maintained.",
     "positive", "Food,Staff,Cleanliness", "train", "Hotel Crown Faisalabad"),

    (24, "Stayed at PC Rawalpindi – great central location, clean rooms, efficient room service, and the Jade Garden Chinese restaurant is exceptional!",
     "positive", "Location,Cleanliness,Staff,Food", "train", "Pearl Continental Rawalpindi"),

    (25, "The Mountain Inn Chitral was a delightful surprise. Peaceful location by the river, very clean, staff spoke good English and were extremely helpful.",
     "positive", "Location,Cleanliness,Staff", "train", "Mountain Inn Chitral"),

    (26, "Nishat Hotel Lahore is exceptional value. The property is beautiful, food at the restaurant is consistently good, staff always smiling, and rooms are immaculate.",
     "positive", "Value for Money,Food,Staff,Cleanliness", "train", "Nishat Hotel Lahore"),

    (27, "Islamabad Club's guest rooms are spacious and clean. The food at their main restaurant is excellent, location is central, and it is remarkably affordable for members.",
     "positive", "Cleanliness,Food,Location,Value for Money", "train", "Islamabad Club"),

    (28, "Greens Hotel Lahore – small but perfectly clean. The owner personally ensures quality, breakfast is fresh and tasty, and the location near MM Alam Road is great.",
     "positive", "Cleanliness,Food,Location,Staff", "train", "Greens Hotel Lahore"),

    (29, "Stayed at Elbow Room Islamabad. Boutique feel, extremely clean, location in F-6 is perfect, and the breakfast is superb. Will definitely be back.",
     "positive", "Cleanliness,Location,Food", "train", "Elbow Room Islamabad"),

    (30, "Hotel Margala Islamabad is a hidden gem. Reasonable pricing, clean rooms, helpful staff, and the panoramic view of the Margala Hills is breathtaking.",
     "positive", "Value for Money,Cleanliness,Staff,Location", "train", "Hotel Margala Islamabad"),

    (31, "The hotel in Nathiagali had perfect cool weather, clean rooms, and the host made us amazing pakoras during rain. True Pakistani hospitality at its finest.",
     "positive", "Cleanliness,Food,Staff", "train", "Nathiagali Hotel"),

    (32, "Airport Hotel Karachi gets 5 stars from me. Super clean, very close to the airport, staff helped with flight queries, and it is excellent value for a transit stay.",
     "positive", "Cleanliness,Location,Staff,Value for Money", "train", "Airport Hotel Karachi"),

    (33, "Hotel Marhaba Rawalpindi – spotlessly clean, incredibly affordable, and staff are warm and welcoming. A proper hidden gem for budget travelers.",
     "positive", "Cleanliness,Value for Money,Staff", "train", "Hotel Marhaba Rawalpindi"),

    (34, "The PC Muzaffarabad has great views of the Jhelum River. Rooms are well-maintained, food is delicious, and the staff is professional and courteous.",
     "positive", "Location,Cleanliness,Food,Staff", "train", "Pearl Continental Muzaffarabad"),

    (35, "Delightful stay at Hotel Rakaposhi Gilgit. Views of Rakaposhi peak, clean rooms, helpful guides organized by the hotel, and very good food.",
     "positive", "Location,Cleanliness,Staff,Food", "train", "Hotel Rakaposhi Gilgit"),

    (36, "Marquis Grand Hotel Lahore – amazing food at their restaurant, spotless rooms, efficient staff, and located in a great area for business meetings.",
     "positive", "Food,Cleanliness,Staff,Location", "train", "Marquis Grand Hotel Lahore"),

    (37, "Hotel De Palma Lahore exceeded expectations. Stylish, clean, excellent breakfast, professional staff, and very reasonable pricing.",
     "positive", "Cleanliness,Food,Staff,Value for Money", "train", "Hotel De Palma Lahore"),

    (38, "Stayed at a traditional haveli hotel in Lahore's old city. Beautifully restored, spotless, food was traditional Lahori, and the location immersed us in culture.",
     "positive", "Cleanliness,Food,Location", "train", "Haveli Hotel Lahore"),

    (39, "Hotel Faran Karachi – budget-friendly, clean rooms, staff is helpful, and the location near Clifton is great for exploring the city.",
     "positive", "Value for Money,Cleanliness,Staff,Location", "train", "Hotel Faran Karachi"),

    (40, "The breakfast spread at Marriott Islamabad is unmatched. Everything fresh, abundant variety, and the coffee is excellent. Rooms are also spotlessly clean.",
     "positive", "Food,Cleanliness", "train", "Marriott Islamabad"),

    # ── TEST SET: Positive (id 41-50) ────────────────────────────────────────
    (41, "Galaxy Hotel Lahore – clean, affordable, good food downstairs, and staff that goes the extra mile. Great for solo travelers on a budget.",
     "positive", "Cleanliness,Value for Money,Food,Staff", "test", "Galaxy Hotel Lahore"),

    (42, "The Grand Hotel Murree – fantastic location on the Mall, clean rooms, good breakfast, and the view is worth waking up early for.",
     "positive", "Location,Cleanliness,Food", "test", "Grand Hotel Murree"),

    (43, "Continental Hotel Faisalabad provides good value. Rooms are clean, staff responsive, food at their dhaba is excellent local cuisine, and the price is right.",
     "positive", "Cleanliness,Staff,Food,Value for Money", "test", "Continental Hotel Faisalabad"),

    (44, "Bahria Town Hotels Lahore – modern, spotless, staff very professional, and food quality at the restaurants is excellent. Highly recommended.",
     "positive", "Cleanliness,Staff,Food", "test", "Bahria Town Hotel Lahore"),

    (45, "Hotel Diplomat Islamabad – central location, clean and comfortable rooms, staff efficient and polite, and pricing is very reasonable.",
     "positive", "Location,Cleanliness,Staff,Value for Money", "test", "Hotel Diplomat Islamabad"),

    (46, "The staff at this hotel in Naran prepared a bonfire for us on a cold night without being asked. Rooms were clean and warm. Absolutely wonderful experience.",
     "positive", "Staff,Cleanliness", "test", "Naran Hotel"),

    (47, "Couldn't have asked for a better stay at Hotel One Peshawar. Spotlessly clean, kind staff, and the location is perfect for the business district.",
     "positive", "Cleanliness,Staff,Location", "test", "Hotel One Peshawar"),

    (48, "The food at Serena Quetta is incredible – rich Balochi cuisine, generous portions, and so fresh. Clean property with very professional staff throughout.",
     "positive", "Food,Cleanliness,Staff", "test", "Serena Hotel Quetta"),

    (49, "Best value hotel in Abbottabad. Incredibly clean for the price, staff genuinely warm, and the mountain air from the room window is a bonus.",
     "positive", "Value for Money,Cleanliness,Staff,Location", "test", "Hotel Abbottabad"),

    (50, "Our corporate retreat at PC Lahore was flawless. Conference team was exceptional, food at every meal was outstanding, and rooms were five-star clean.",
     "positive", "Staff,Food,Cleanliness", "test", "Pearl Continental Lahore"),

    # ── NEGATIVE (id 51-80) ──────────────────────────────────────────────────
    (51, "Absolutely disgusted by the state of this Lahore hotel. The bathroom was filthy, there was mold on the walls, and sheets had clearly not been changed. Never again!",
     "negative", "Cleanliness", "train", "Budget Hotel Lahore"),

    (52, "The staff at this hotel in Karachi were shockingly rude. My complaints were ignored, and when I asked for towels, I was made to feel like I was begging.",
     "negative", "Staff", "train", "Budget Hotel Karachi"),

    (53, "Overpriced and underwhelming. Paid 15,000 for a room that looked nothing like the pictures. The food was stale, cold, and completely tasteless.",
     "negative", "Value for Money,Food", "train", "Islamabad Hotel"),

    (54, "The guesthouse near Naran had a sewage smell throughout. The bathroom tiles were cracked and dirty. Completely ruined our family vacation.",
     "negative", "Cleanliness", "train", "Naran Guesthouse"),

    (55, "Worst hotel experience in Islamabad. Located in an unsafe area, staff were unapproachable, and the food gave us food poisoning. Avoid at all costs.",
     "negative", "Location,Staff,Food", "train", "Islamabad Hotel"),

    (56, "The so-called luxury hotel in Murree had broken heaters in December! When we complained, staff were completely dismissive. The food was terrible too. Total rip-off.",
     "negative", "Staff,Food,Value for Money", "train", "Murree Hotel"),

    (57, "Cockroaches in the kitchen area, dusty curtains, stained carpets. This place in Rawalpindi calls itself 3 stars but deserves absolutely zero.",
     "negative", "Cleanliness", "train", "Rawalpindi Hotel"),

    (58, "The hotel near Lahore's Gulberg was impossibly loud – street noise all night with single-pane windows. Staff offered no solution and were rude about it.",
     "negative", "Location,Staff", "train", "Gulberg Hotel Lahore"),

    (59, "Room service took 2 hours and arrived cold. When I called the front desk, they hung up on me. The rooms were also dirty and smelled of cigarettes.",
     "negative", "Staff,Cleanliness,Food", "train", "Karachi Hotel"),

    (60, "Terrible value for money. For the price, I expected clean rooms – instead I got a mattress with visible stains, broken AC, and a cockroach as a roommate.",
     "negative", "Value for Money,Cleanliness", "train", "Lahore Hotel"),

    (61, "The food at this Karachi hotel was an absolute disaster – undercooked chicken, stale bread, and expired milk in the breakfast. Made the whole family sick.",
     "negative", "Food", "train", "Karachi Hotel"),

    (62, "Hotel near Swat city center – location sounds great but it is next to a noisy market. The rooms were dirty, staff disinterested, and overpriced.",
     "negative", "Location,Cleanliness,Staff,Value for Money", "train", "Swat Hotel"),

    (63, "Checked into a Faisalabad hotel to find my room had clearly not been cleaned after the previous guest. Hair everywhere, used toiletries still in the bathroom.",
     "negative", "Cleanliness", "train", "Faisalabad Hotel"),

    (64, "Staff at this Multan hotel were completely untrained. They could not answer basic questions, were slow with check-in, and dismissive of our every request.",
     "negative", "Staff", "train", "Multan Hotel"),

    (65, "The restaurant at this Islamabad hotel charged premium prices for terrible food. Soggy kebabs, watery curry, and stale naan. Completely unacceptable.",
     "negative", "Food,Value for Money", "train", "Islamabad Hotel"),

    (66, "Our room in Gilgit guesthouse had no hot water despite promises. The room was cold, windows did not close properly, and the food was barely edible.",
     "negative", "Cleanliness,Food", "train", "Gilgit Guesthouse"),

    (67, "The location of this Karachi hotel was dangerously close to a flooded street. No warning given. Rooms were musty and smelled of dampness throughout.",
     "negative", "Location,Cleanliness", "train", "Karachi Hotel"),

    (68, "Hotel in Abbottabad – reception staff were on their phones the entire time, ignored us for 20 minutes at check-in. Completely unprofessional.",
     "negative", "Staff", "train", "Abbottabad Hotel"),

    (69, "Extremely disappointed with the cleanliness. The pool area was green with algae, the changing rooms were disgusting, and staff did nothing about it.",
     "negative", "Cleanliness,Staff", "train", "Lahore Hotel"),

    (70, "Paid for a sea-view room in Karachi and got a view of a construction site. Noisy all day, dusty room, and staff refused any accommodation.",
     "negative", "Location,Cleanliness,Staff,Value for Money", "train", "Karachi Hotel"),

    (71, "The buffet at this hotel was a complete waste of money. Half the dishes were empty by 8 AM, the rest were cold, and the coffee machine was broken.",
     "negative", "Food,Value for Money", "train", "Rawalpindi Hotel"),

    (72, "The hotel claimed to be near the airport but was 45 minutes away. The rooms were old, dirty, and the air conditioning did not work at all.",
     "negative", "Location,Cleanliness,Value for Money", "train", "Karachi Hotel"),

    (73, "Staff at reception were on personal phone calls when we arrived. Room had dead insects on windowsill. The included breakfast was just plain bread and weak tea.",
     "negative", "Staff,Cleanliness,Food", "train", "Islamabad Hotel"),

    (74, "Worst hotel in Lahore I have ever stayed at. Mattress was lumpy, sheets had holes, bathroom door would not lock, and management did not care at all.",
     "negative", "Cleanliness,Staff", "train", "Lahore Hotel"),

    (75, "The food poisoning I got from this Karachi hotel restaurant put me in hospital. The kitchen looked filthy when I accidentally walked by.",
     "negative", "Food,Cleanliness", "train", "Karachi Hotel"),

    (76, "Overcharged us at checkout with hidden fees. When we questioned the bill, staff became aggressive. Location was also far from everything we needed.",
     "negative", "Value for Money,Staff,Location", "train", "Lahore Hotel"),

    (77, "Room smelled like stale smoke, no ventilation, and the window view was of a brick wall. For 8,000 a night this was criminal robbery.",
     "negative", "Cleanliness,Value for Money", "train", "Rawalpindi Hotel"),

    (78, "Hotel near Saddar Karachi – felt completely unsafe. Broken locks on doors, poor lighting in corridors, and staff were nowhere to be found at night.",
     "negative", "Location,Staff,Cleanliness", "train", "Saddar Hotel Karachi"),

    (79, "The dining room at this Rawalpindi hotel was infested with flies. The food was cold and poorly cooked. Complained multiple times – zero action taken.",
     "negative", "Food,Cleanliness,Staff", "train", "Rawalpindi Hotel"),

    (80, "Booked based on website photos but arrived to a completely different, run-down property. Classic bait-and-switch. Rooms were dirty and staff were rude.",
     "negative", "Cleanliness,Staff,Value for Money", "train", "Lahore Hotel"),

    # ── TEST SET: Negative (id 81-90) ────────────────────────────────────────
    (81, "The noise from the highway made sleep impossible. No soundproofing, no curtains that blocked light. Not worth a quarter of what we paid.",
     "negative", "Location,Value for Money", "test", "Islamabad Hotel"),

    (82, "Room had mysterious water stains on ceiling, mold around shower area, and a carpet that was wet. Staff acknowledged it but offered absolutely no solution.",
     "negative", "Cleanliness,Staff", "test", "Karachi Hotel"),

    (83, "Breakfast was a disaster – cold scrambled eggs, stale croissants, and juice that tasted like it was from years ago. Inedible and overpriced.",
     "negative", "Food,Value for Money", "test", "Lahore Hotel"),

    (84, "The hotel claimed WiFi throughout but there was zero signal in the room. When we complained, staff said it depends on the weather. Completely unacceptable.",
     "negative", "Staff,Value for Money", "test", "Murree Hotel"),

    (85, "Staff was dismissive of our dietary requests despite us notifying in advance. The food arrived with meat in what was supposed to be a vegetarian dish.",
     "negative", "Staff,Food", "test", "Islamabad Hotel"),

    (86, "This resort near Nathiagali was a complete fraud. Broken facilities, dirty rooms, inedible food, rude staff, and no refund despite legitimate complaints.",
     "negative", "Cleanliness,Food,Staff,Value for Money", "test", "Nathiagali Resort"),

    (87, "The hotel in Peshawar's old city area – rooms were not cleaned properly and the shared bathroom was a genuine health hazard. Unhygienic and unacceptable.",
     "negative", "Cleanliness", "test", "Peshawar Hotel"),

    (88, "Reception staff gave us the wrong room – occupied by another guest! Then laughed about it instead of apologizing. Completely unacceptable behavior.",
     "negative", "Staff", "test", "Islamabad Hotel"),

    (89, "Food quality has severely declined since our last visit. Overpriced menu, small portions, poor taste, and slow service. Very disappointing experience.",
     "negative", "Food,Value for Money", "test", "Lahore Hotel"),

    (90, "Bathroom had no hot water for our entire 3-day stay despite daily complaints. Staff kept promising to fix it but never did. Total disregard for guests.",
     "negative", "Cleanliness,Staff", "test", "Karachi Hotel"),

    # ── NEUTRAL (id 91-120) ──────────────────────────────────────────────────
    (91, "Hotel in Lahore city center. Location is good, rooms are average – nothing spectacular but clean enough. Food is basic but filling. Decent for the price.",
     "neutral", "Location,Cleanliness,Food,Value for Money", "train", "Lahore Hotel"),

    (92, "PC Lahore is a well-known name but I found it slightly overpriced for what they offer now. Service is okay, rooms are clean, food was average.",
     "neutral", "Value for Money,Cleanliness,Food", "train", "Pearl Continental Lahore"),

    (93, "The guesthouse in Murree was acceptable. Not the cleanest place but not terrible either. Staff tried their best. Location near the mall is convenient.",
     "neutral", "Cleanliness,Staff,Location", "train", "Murree Guesthouse"),

    (94, "Marriott Karachi – checked in, room was as expected. Breakfast was decent, staff polite but not exceptionally helpful. Standard luxury hotel experience.",
     "neutral", "Food,Staff", "train", "Marriott Karachi"),

    (95, "Hotel in Islamabad Blue Area – location is good, rooms are functional. Nothing remarkable about the food or service. Gets the job done for a business trip.",
     "neutral", "Location,Food,Staff", "train", "Islamabad Hotel"),

    (96, "Mid-range hotel in Rawalpindi. Clean enough, staff okay, food was nothing to write home about. Fair value for the price point.",
     "neutral", "Cleanliness,Staff,Food,Value for Money", "train", "Rawalpindi Hotel"),

    (97, "Stayed at a hotel near Lahore airport. Convenient location for an early flight. Room was basic but clean. Breakfast was standard hotel fare – nothing special.",
     "neutral", "Location,Cleanliness,Food", "train", "Lahore Airport Hotel"),

    (98, "The hotel in Abbottabad had an okay location. Rooms were clean but furniture was dated. Staff was polite. Food was average local cuisine.",
     "neutral", "Location,Cleanliness,Staff,Food", "train", "Abbottabad Hotel"),

    (99, "Decent stay at Hotel One Peshawar. Clean rooms, basic breakfast, helpful staff. Nothing exceptional but a reliable, safe option in the city.",
     "neutral", "Cleanliness,Food,Staff", "train", "Hotel One Peshawar"),

    (100, "Ramada Lahore – good location near Gulberg. Service is average, food is decent. Room was clean but felt dated. Okay for a business trip.",
     "neutral", "Location,Staff,Food,Cleanliness", "train", "Ramada Lahore"),

    (101, "Hotel in Faisalabad – functional stay. Room not the largest but adequately clean. Staff were okay. Food at the restaurant was so-so. Fair price.",
     "neutral", "Cleanliness,Staff,Food,Value for Money", "train", "Faisalabad Hotel"),

    (102, "Guesthouse in Chitral – basic amenities, clean enough, staff spoke limited English but tried to help. Food was local and adequate. Simple but acceptable.",
     "neutral", "Cleanliness,Staff,Food", "train", "Chitral Guesthouse"),

    (103, "PC Bhurban is nice but I expected more for the price. Rooms are clean and views are great, but service has slipped compared to before.",
     "neutral", "Cleanliness,Location,Value for Money,Staff", "train", "Pearl Continental Bhurban"),

    (104, "Hotel in Karachi DHA – decent option. Clean room, working AC, okay food, average staff. Nothing to rave about but nothing to complain about either.",
     "neutral", "Cleanliness,Food,Staff", "train", "DHA Hotel Karachi"),

    (105, "Stayed in Gilgit at a mid-range hotel. The location is okay, rooms are basic but clean, and the food is standard Pakistani fare. Gets the job done.",
     "neutral", "Location,Cleanliness,Food", "train", "Gilgit Hotel"),

    (106, "Average experience at this Multan hotel. Room was clean, staff was present but not proactive, food was mediocre. Nothing particularly good or bad.",
     "neutral", "Cleanliness,Staff,Food", "train", "Multan Hotel"),

    (107, "Hotel in Islamabad for a conference. Room was fine, breakfast was okay, location worked for our needs. A professional but forgettable experience.",
     "neutral", "Cleanliness,Food,Location", "train", "Islamabad Hotel"),

    (108, "Guesthouse near Kalash Valley – basic but clean. Host was helpful for local arrangements. Food was simple. Good enough for an adventure base camp.",
     "neutral", "Cleanliness,Staff,Food", "train", "Kalash Guesthouse"),

    (109, "Business hotel in Lahore. Functional, clean, polite staff. Food at their café is uninspiring but edible. Location convenient for commercial area meetings.",
     "neutral", "Cleanliness,Staff,Food,Location", "train", "Lahore Business Hotel"),

    (110, "Hotel in Hyderabad – room was average, clean but worn. Staff okay. Food was standard. Reasonably priced for what it is.",
     "neutral", "Cleanliness,Staff,Food,Value for Money", "train", "Hyderabad Hotel"),

    (111, "The resort in Shogran was beautiful in terms of location but the facilities were underwhelming for the price. Rooms were okay, food was passable.",
     "neutral", "Location,Cleanliness,Food,Value for Money", "train", "Shogran Resort"),

    (112, "Hotel Serena Quetta – good location and clean rooms, but the food was disappointing for a Serena property. Staff was professional enough.",
     "neutral", "Location,Cleanliness,Food,Staff", "train", "Serena Hotel Quetta"),

    (113, "Average hotel near Karachi's Saddar area. Location is central, rooms are small but clean, staff manages but does not excel. Fair for the rate.",
     "neutral", "Location,Cleanliness,Staff,Value for Money", "train", "Saddar Hotel Karachi"),

    (114, "Hotel in Lahore's Johar Town. Convenient for families visiting relatives. Clean enough, food is nothing special, staff polite but service is basic.",
     "neutral", "Cleanliness,Food,Staff", "train", "Johar Town Hotel Lahore"),

    (115, "Standard hotel experience in Gujranwala. Room was clean, staff functional, food was average desi fare. Value for money is okay.",
     "neutral", "Cleanliness,Staff,Food,Value for Money", "train", "Gujranwala Hotel"),

    (116, "Hotel near Khunjerab Pass – very basic, clean in the essentials, food limited to simple meals. Staff kind but limited in service capacity. Expected remotely.",
     "neutral", "Cleanliness,Food,Staff", "train", "Khunjerab Hotel"),

    (117, "Stayed at a mid-tier hotel in Bahawalpur. Clean rooms, standard food, polite staff. Location was okay for visiting Lal Suhanra. Nothing memorable.",
     "neutral", "Cleanliness,Food,Staff,Location", "train", "Bahawalpur Hotel"),

    (118, "Hotel in Mingora Swat – decent base for exploring. Location is central, rooms are basic but clean, food is average local cuisine. Gets the job done.",
     "neutral", "Location,Cleanliness,Food", "train", "Mingora Hotel"),

    (119, "Average experience overall. The hotel in Murree was acceptable – clean sheets, decent heating, staff not particularly friendly but not rude. Standard stuff.",
     "neutral", "Cleanliness,Staff", "train", "Murree Hotel"),

    (120, "Hotel in Sialkot – clean and functional. Staff are polite, food is basic, and the location near the industrial area suits business travelers. Nothing spectacular.",
     "neutral", "Cleanliness,Staff,Food,Location", "train", "Sialkot Hotel"),

    # ── TEST SET: Neutral (id 121-125) ───────────────────────────────────────
    (121, "Guesthouse in Besham – average at best. The room was neither particularly clean nor dirty. Food was mediocre and the service was indifferent. Nothing to complain about but nothing to praise either.",
     "neutral", "Cleanliness,Food,Staff", "test", "Besham Guesthouse"),

    (122, "Hotel in Turbat – mixed experience. Rooms were so-so, staff were okay but not helpful, and the food was unremarkable. Average stay for a transit stop.",
     "neutral", "Cleanliness,Staff,Food", "test", "Turbat Hotel"),

    (123, "Business stay in Lahore at a mid-range property. The room was passable, food mediocre, service neither impressive nor terrible. Forgettable and unremarkable overall.",
     "neutral", "Cleanliness,Food,Staff,Location", "test", "Lahore Hotel"),

    (124, "Hotel in Sukkur – not bad but not good either. Rooms are average, staff are indifferent, and the food is uninspiring. Acceptable but unremarkable.",
     "neutral", "Cleanliness,Staff,Food", "test", "Sukkur Hotel"),

    (125, "Stayed near Thandiani – the guesthouse was mediocre despite the scenic surroundings. Average room, bland food, minimal staff interaction. Just okay.",
     "neutral", "Location,Cleanliness,Food", "test", "Thandiani Guesthouse"),
]


def generate():
    out_path = os.path.join(os.path.dirname(__file__), "reviews_dataset.csv")
    fieldnames = ["id", "review_text", "sentiment", "themes", "split", "location", "source"]

    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in REVIEWS:
            writer.writerow({
                "id": row[0],
                "review_text": row[1],
                "sentiment": row[2],
                "themes": row[3],
                "split": row[4],
                "location": row[5],
                "source": "simulated",
            })
    print(f"✅  Saved {len(REVIEWS)} reviews → {out_path}")


if __name__ == "__main__":
    generate()
