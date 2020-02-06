
# Tools for editing milpac information.

'''
Structure
    class add():
        def serviceRecord(text, date, citation=False)
        def awards(award, date, citation, details=False)
        def uniform(file, deleteCurrent=True)
    class edit()
        def user(rank=False, position=False, secondaryPositions=False, enlistmentDate=False, promotionDate=False) # All others should not be changed via script
        def serviceRecord(text=False, date=False, citation=False)
        def award(award=False, date=False, citation=False, details=False)
    class remove()
        def serviceRecord()
        def award()
'''