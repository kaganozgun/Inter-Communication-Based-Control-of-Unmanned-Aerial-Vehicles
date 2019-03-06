# Inter-Communication-Based-Control-of-Unmanned-Aerial-Vehicles
Graduation project of computer engineering 

With the rapid development of technology in recent years, the size of computer com-
ponents has become very small, and these components have become quite reachable
ﬁgures as the production costs have decreased. Thanks to these developments, some
of the devices that were supposed to be used only for military purposes in advance can
now be sold for personal use. Unmanned Aerial Vehicle (UAV) can be given as an ex-
ample for that kind of devices. Today, almost all of the technology stores in the world
have UAVs oﬀered for sale. There have been many developments on the software side
as well as improvements on the hardware side. Developing UAV projects carried out
large corporations as open source code and sharing these codes with everyone, people
who want to have information about autonomous systems and work on this ﬁeld have
gained access to similar work.
Nowadays, UAVs are being used instead of niches that are based on human power
or made with large and complex tools. For example, UAVs can be used on search and
rescue tasks after natural disasters such as earthquake, ﬁre or ﬂood. UAVs can quickly
scan the area and can have access to victims of natural disasters. Additionally UAVs
are suitable for optimization tasks such as logistic. Using UAVs on optimization of
transportation can decrease the time, energy and cost of the tasks.
Usage of the UAVs have some critical problems and bottlenecks. The area scanned
with the UAVs should be done as soon as possible and with as high accuracy as pos-
sible. For this purpose, this task has been to be conducted with multiple UAVs, but
fulﬁlling this task with multiple UAVs creates a bottleneck on the communication chan-
nels. In order to perform such a task with more than one UAV, communication both
between the UAVs and between the UAVs and the ground station must be safe and
secure. If communication between UAVs and ground station is lost, the UAVs stop
their tasks for security and land on a safe area by following predetermined protocols.
This project is to solve the problem of communication between the intended UAVs
using centralized or decentralized communication techniques used in combination. As
a proof of concept, it is aimed to complete the tasks of two UAVs scanning the area
by establishing communication with both the ground station and each other.At the beginning of the mission, the ﬁeld information determined by the ground sta-
tion is sent to both UAVs. The paths that the UAVs follow in the designated area
are transferred to the UAVs in a graph-based data structure. Then the UAVs start
to conduct their duties. The UAVs mark to indicate that this point has been reached
when the target points are reached. If the UAVs are in communication with the ground
station, they transmit information about the points they reach to the ground station.
In addition, the UAVs transmit this information amongst themselves in the range re-
quired for communication on the map. In this case, the UAVs can communicate with
each other and determine which areas are scanned. When two UAVs complete their
tasks, they transfer the acquired information to each other and become ready for the
next relative.
Field scanning task can be done by using diﬀerent algorithms. The three primary
methods used in the project and the variations of these methods will be used. In these
three methods, the selection of routes to be followed by UAVs is made diﬀerently. The
ﬁrst method, the zigzag method, is performed by linear paths separated horizontally
or vertically. In the second method, the spiral method, the area to be scanned is to be
made by dividing it into the interior and gradually decreasing areas. With this method,
when the UAV arrives at the middle point of the area, which begins to scan from an
outside edge of the area, it will complete its mission. The third method will be done
by randomly selecting the route that the UAV will follow from the point closest to the
position of the UAV. In this way, if all the points around the UAV are travelling, the
mission of the UAV will be terminated.
In the testing phase of the project performance of the algorithms are compared us-
ing two UAVs and using the single UAV. Performance criteria of diﬀerent test cases
are determined using area coverage information, time cost of the searching operation
and energy consumption of the UAVs.

You can access the complete thesis from the link below.
https://drive.google.com/open?id=1D_qJWrc4-dxfKhsa8sA1u34HESsKv3wk
