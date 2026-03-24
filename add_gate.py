with open('/var/www/shortfactory.shop/alive/studio/online_server.py', 'r') as f:
    content = f.read()

old = '            if len(user_msg) > 4000:\n                user_msg = user_msg[:4000]\n\n            # Large input preprocessing'

new = ('            if len(user_msg) > 4000:\n'
       '                user_msg = user_msg[:4000]\n\n'
       '            # === RANK GATE - CORPORAL+ only ===\n'
       '            req_key = body.get(\'api_key\', \'\')\n'
       '            req_credits = int(body.get(\'credits\', 0) or 0)\n'
       '            key_valid = (req_key == CORTEX_API_KEY)\n'
       '            rank_valid = (req_credits >= CORTEX_RANK_GATE)\n'
       '            if not key_valid:\n'
       '                self._json_response({\'ok\': True, \'text\': "I\'m CORTEX. I don\'t talk to strangers. Earn your rank at shortfactory.shop.", \'locked\': True, \'locked_reason\': \'api_key\'})\n'
       '                return\n'
       '            if not rank_valid:\n'
       '                self._json_response({\'ok\': True, \'text\': "I\'m CORTEX. Reach CORPORAL rank to unlock me. 3,000 credits. Contribute to the empire and come back.", \'locked\': True, \'locked_reason\': \'rank\', \'credits_needed\': CORTEX_RANK_GATE - req_credits})\n'
       '                return\n\n'
       '            # Large input preprocessing')

if old in content:
    content = content.replace(old, new, 1)
    with open('/var/www/shortfactory.shop/alive/studio/online_server.py', 'w') as f:
        f.write(content)
    print('Gate inserted OK')
else:
    print('ERROR: pattern not found')
    # debug - show what is around line 377
    lines = content.split('\n')
    for i, l in enumerate(lines[374:382], 375):
        print(f'{i}: {repr(l)}')
