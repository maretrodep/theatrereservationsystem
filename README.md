# Theatre reservation system
A theatre reservation system as university project  
For this project flask is used for the backend with sqlalchemy as ORM  
For frontend simple bootstrap is used with flask templating system

# Features
- Admin panel
- Owner panel
- User panel

# Specifications
The system should allow people to view the upcoming programme of events, select one and then select their desired seating.  The theatre has 3 seating locations as follows:  
## Stalls
- **AA – DD**: +200% (Matinee) / +250% (Evening)
- **A – M**: +150% (Matinee) / +175% (Evening)
- **P - V**: +100% (Matinee) / +150% (Evening)

## Circle
- **Row A seats 1-6, 71-76**: +150% (Matinee) / +175% (Evening)
- **Row B seats 1-8, 75-82**: +125% (Matinee) / +150% (Evening)
- **Row C seats 1-8, 82-89**: +125% (Matinee) / +150% (Evening)
- **Row A seats 7-27, 50-70**: +125% (Matinee) / +150% (Evening)
- **Row B seats 9-31, 52-74**: +125% (Matinee) / +150% (Evening)
- **Row C seats 9-34, 56-81**: +125% (Matinee) / +150% (Evening)
- **Row A seats 28-49**: +210% (Matinee) / +220% (Evening)
- **Row B seats 32-51**: +210% (Matinee) / +220% (Evening)
- **Row C seats 35-55**: +210% (Matinee) / +220% (Evening)

## Upper Circle
- **Row A seats 1-6, 83-88**: +80% (Matinee) / +100% (Evening)
- **Row B seats 1-8, 86-93**: +80% (Matinee) / +100% (Evening)
- **Row C seats 1-8, 69-76**: +80% (Matinee) / +100% (Evening)
- **Row A seats 7-32, 57-82**: +50% (Matinee) / +70% (Evening)
- **Row B seats 9-34, 80-85**: +50% (Matinee) / +70% (Evening)
- **Row C seats 9-24, 53-68**: +50% (Matinee) / +70% (Evening)
- **Row A seats 33-56**: +75% (Matinee) / +100% (Evening)
- **Row B seats 35-59**: +75% (Matinee) / +100% (Evening)
- **All other upper circle**: No changes (Base)
  
There are concessionary rates for under 16’s and over 70’s, and large parties (bookings of more than 10 people); all concessions are not compound, the best concession is taken and applied.  The theatre also offers a loyalty card which entitles members to discount of 10% per ticket and the ability to reserve seats 1 week before the official release date.

