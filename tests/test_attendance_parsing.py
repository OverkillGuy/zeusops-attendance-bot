"""Check the OP DELIMITER parsing works"""

import json

from zeusops_attendance_bot.models import AttendanceMsg
from zeusops_attendance_bot.parsing import split_ops_flagged

MSGS = """[{"id":977644183361814500,"author_display":"tollmannd","author_id":266696844065636350,"message":"A1: Toll(L), BLoaf, Adam, Jib","created_at":"2022-05-21T18:48:57.064000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":977644205885247500,"author_display":"MikeAngel","author_id":344685908311670800,"message":"ASL: Angel(L), Floggy, Duggy, Sterling","created_at":"2022-05-21T18:49:02.434000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":977644213988643000,"author_display":"Eowalas","author_id":692789330149769300,"message":"HQ1PLT: Johnston(L), Recon","created_at":"2022-05-21T18:49:04.366000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":977644313540440000,"author_display":"Dr. Madog II","author_id":729666211822174200,"message":"Z1 - Asimov, Barr","created_at":"2022-05-21T18:49:28.101000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":977644658064760800,"author_display":"Solo Wing Pixy","author_id":417061673019506700,"message":"BSL:Pixy(L), Black, Miller, Tao, Walla, Lefty, Rajan. Demonaki","created_at":"2022-05-21T18:50:50.242000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":977645846537597000,"author_display":"Better Goose","author_id":319101566227578900,"message":"HQCO: Goose","created_at":"2022-05-21T18:55:33.596000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":978006995523207200,"author_display":"DaSchmitt","author_id":232091553806417920,"message":"A: Schmitt (L), Lietuvis, Tao, Pavelow, Barr","created_at":"2022-05-22T18:50:38.224000+00:00","edited_at":null,"flags":["OP_DELIMITER"],"is_split":true},{"id":978007033062228000,"author_display":"Snejk","author_id":393793204413268000,"message":"BSL: Venom(L), Demonaki, Roth, Duggy, Toast","created_at":"2022-05-22T18:50:47.174000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":978007259093270700,"author_display":"Dr. Madog II","author_id":729666211822174200,"message":"L1 - Asimov","created_at":"2022-05-22T18:51:41.064000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":978007259093270700,"author_display":"Dr. Madog II","author_id":729666211822174200,"message":"T1 - Walla","created_at":"2022-05-22T18:51:41.064000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":978008116811686000,"author_display":"Better Goose","author_id":319101566227578900,"message":"HQ1PLT: Goose (L), Johnston","created_at":"2022-05-22T18:55:05.560000+00:00","edited_at":null,"flags":[],"is_split":true},{"id":978008138697560000,"author_display":"Solo Wing Pixy","author_id":417061673019506700,"message":"HQCO: Pixy(Mod)","created_at":"2022-05-22T18:55:10.778000+00:00","edited_at":null,"flags":[],"is_split":true}]"""

msgs_dict: list[dict] = json.loads(MSGS)
msgs_obj: list[AttendanceMsg] = [AttendanceMsg.parse_obj(msg) for msg in msgs_dict]

SPLIT_INDEX = 6


def test_split_ops_flagging():
    """Check the flagged ops get split appropriately"""
    # Given a list of AttendanceMsg
    # And the list was grouped by separator message
    # And a message contains an OP delimiter flag
    # But the list wasn't split by flag delimiter
    # When I split by flag delimiter
    ops_split = split_ops_flagged([msgs_obj])
    # Then the messages are split based on operation
    assert ops_split == [
        msgs_obj[:SPLIT_INDEX],
        msgs_obj[SPLIT_INDEX:],
    ], "Messages should be split properly"
