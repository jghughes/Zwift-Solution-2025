using System;
using System.Collections.Generic;
using System.Linq;
using Jgh.SymbolsStringsConstants.Mar2022;
using NetStd.Goodies.Mar2022;
using Rezultz.DataTypes.Nov2023.PortalHubItems;
using Rezultz.DataTypes.Nov2023.SeasonAndSeriesProfileItems;
using Rezultz.Library01.Mar2024.Repository_interfaces;

namespace Rezultz.Library01.Mar2024.Repositories
{
    public class ParticipantDatabase
    {
        #region public methods

        public static string ToAgeCategoryDescriptionFromBirthYear(int yearOfBirth, AgeGroupSpecificationItem[] ageGroupSpecifications)
        {
            if (ageGroupSpecifications is null || !ageGroupSpecifications.Any())
                return string.Empty;

            var now = DateTime.Now;

            var age = now.Year - yearOfBirth;

            var ageGroupSpecification = ageGroupSpecifications
                .Where(z => z is not null)
                .Where(z => age >= z.AgeLower)
                .FirstOrDefault(z => age <= z.AgeUpper);

            if (ageGroupSpecification is null || string.IsNullOrWhiteSpace(ageGroupSpecification.Label))
                return string.Empty;

            var answer = ageGroupSpecification.Label;

            return answer;
        }

        public static int ToAgeFromBirthYear(int yearOfBirth)
        {

            var now = DateTime.Now;

            var age = now.Year - yearOfBirth;

            return age;
        }

        #endregion

        #region load database - HEAP POWERFUL

        public void LoadDatabaseV2(IRepositoryOfHubStyleEntries<ParticipantHubItem> repositoryOfParticipants)
        {
            // the expectation here is that the participantHubItems will be raw data
            // quite normal and commonplace for items to be null, and or participantMasterList to be null, and/or categoryToGroupStartMap to be null. nothing more to do. bale

            #region null checks

            if (repositoryOfParticipants is null)
            {
                _repositoryIsBootstrapped = true;

                return;
            }

            _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers = repositoryOfParticipants.GetYoungestDescendentOfEachOriginatingItemGuidIncludingDitches();

            if (_backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers is null)
            {
                _repositoryIsBootstrapped = true;

                return;
            }

            #endregion
            
            #region annotate entries featuring missing row details - if any

            foreach (var row in _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers.Where(z => z is not null))
            {
                row.Comment = string.Empty; // clear any previous work

                if (string.IsNullOrWhiteSpace(row.Gender)) row.Comment = JghString.ConcatAsSentences(row.Comment, "Gender not specified.");

                var yearNow = DateTime.UtcNow.Year;
                if (yearNow - row.BirthYear > 80) row.Comment = JghString.ConcatAsSentences(row.Comment, "Participant older than 80.");
                if (row.BirthYear - yearNow >= 0) row.Comment = JghString.ConcatAsSentences(row.Comment, "Year of birth cannot be now or in the future.");

                if (string.IsNullOrWhiteSpace(row.RaceGroupBeforeTransition)) row.Comment = JghString.ConcatAsSentences(row.Comment, "Race group not specified.");


                if (string.IsNullOrWhiteSpace(row.Bib))
                    row.Comment = JghString.ConcatAsSentences(row.Comment, "Blank ID.");
                else if (JghString.JghStartsWith(Symbols.SymbolUnspecified, row.Bib)) row.Comment = JghString.ConcatAsSentences(row.Comment, "ID not specified.");


                if (string.IsNullOrWhiteSpace(JghString.Concat(row.FirstName, row.MiddleInitial, row.LastName))) row.Comment = JghString.ConcatAsSentences(row.Comment, "Blank names.");

                if (string.IsNullOrWhiteSpace(JghString.Concat(row.FirstName, row.MiddleInitial, row.LastName)))
                    if (JghString.JghStartsWith(Symbols.SymbolUnspecified, row.Bib) || string.IsNullOrWhiteSpace(row.Bib))
                        row.Comment = JghString.ConcatAsSentences(row.Comment, "ID blank or unspecified and names blank.");
            }

            #endregion

            #region diagnose and annotate entries featuring duplicate identifiers - if any

            _diagnosedAsDuplicateIdentifiers = DiagnoseDuplicateIdentifiers();

            #endregion

            #region diagnose and annotate entries featuring duplicate names - if any

            _diagnosedAsDuplicateNames = DiagnoseDuplicateNames();

            #endregion

            _backingStoreMasterDictionaryOfParticipantsKeyedByIdentifier = ObtainMostRecentEntryForEachIdentifierOmittingDitchesAndDuplicatesOrderedByWhenTouched();

            _repositoryIsBootstrapped = true;
        }
    
        #endregion

        #region constants

        private bool _repositoryIsBootstrapped;

        /// <summary>
        ///     Allow max 6 days for people to contact organiser to correct their details after a race (or backdate a change of race category)
        ///     I choose this amount because it brings us to midnight the day before the following weekly event
        /// </summary>
        //private const int GracePeriodForCorrectingOrChangingRaceCategoryInDays = 6;

        #endregion

        #region fields

        private ParticipantHubItem[] _diagnosedAsDuplicateNames = [];

        private ParticipantHubItem[] _diagnosedAsDuplicateIdentifiers = [];

        private Dictionary<string, ParticipantHubItem> _backingStoreMasterDictionaryOfParticipantsKeyedByIdentifier = new();

        private ParticipantHubItem[] _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers = [];

        #endregion

        #region methods - access data

        /// <summary>
        ///     This is the governing master list.
        ///     Use this for enumerations.
        ///     Ordered by name.
        ///     Ditches are excluded, which in the opposite of timestamps
        ///     NB. for clashing duplicate identifiers we use the most recent entry in the HubItem repository.
        /// </summary>
        /// <returns></returns>
        public ParticipantHubItem[] GetMasterList()
        {
            var answer = _backingStoreMasterDictionaryOfParticipantsKeyedByIdentifier.Select(z => z.Value)
                .Where(z => !z.MustDitchOriginatingItem)
                .OrderBy(z => z.LastName)
                .ThenBy(z => z.FirstName)
                .ThenBy(z => z.MiddleInitial)
                .ThenBy(z => z.Bib)
                .ThenByDescending(z => z.WhenTouchedBinaryFormat);

            return answer.ToArray();
        }

        /// <summary>
        ///     Most recent entry with a specific identifier is king. Previous entries are rightly or wrongly smothered.
        ///     returns null if this identifier is non-existent.
        /// </summary>
        /// <returns></returns>
        public ParticipantHubItem GetParticipantFromMasterList(string identifierAsKey)
        {
            if (!_repositoryIsBootstrapped)
                return null;

            var valueDoesExist = _backingStoreMasterDictionaryOfParticipantsKeyedByIdentifier.TryGetValue(identifierAsKey, out var answer);

            return valueDoesExist ? answer : null;
        }

        /// <summary>
        ///     This is the datagrid of the ParticipantHubItem repository.
        ///     Reflects the youngest entry for each OriginatingItemGuid.
        ///     Includes ditches and duplicate identifiers.
        ///     Ordered by most recently touched first.
        /// </summary>
        /// <returns></returns>
        public ParticipantHubItem[] GetSurfaceViewOfUnderlyingHubItemRepository()
        {
            var answer = _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers
                .OrderByDescending(z => z.WhenTouchedBinaryFormat);

            return answer.ToArray();
        }

        public ParticipantHubItem[] GetDitches()
        {
            return _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers.Where(z => z.MustDitchOriginatingItem).ToArray();
        }

        public ParticipantHubItem[] GetDuplicateIdentifiers()
        {
            return _diagnosedAsDuplicateIdentifiers;
        }

        public ParticipantHubItem[] GetDuplicatePeople()
        {
            return _diagnosedAsDuplicateNames;
        }

        public ParticipantHubItem[] GetParticipantsWhoOstensiblyTransitionedFromOneRaceGroupToAnother()
        {
            return GetMasterList().Where(participantKvp => participantKvp.RaceGroupBeforeTransition != participantKvp.RaceGroupAfterTransition).ToArray();
        }


        #endregion

        #region helpers

        private ParticipantHubItem[] DiagnoseDuplicateIdentifiers()
        {
            List<ParticipantHubItem> answer = [];

            JghListDictionary<string, ParticipantHubItem> listDictionaryGroupedByIdentifier = HubItemBase.ToListDictionaryGroupedByBib(_backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers.Where(z => !z.MustDitchOriginatingItem).ToArray());

            List<ParticipantHubItem> repeatedIdentifiers = [];

            foreach (var identifierKvp in listDictionaryGroupedByIdentifier)
                if (identifierKvp.Value.Count > 1)
                    repeatedIdentifiers.AddRange(identifierKvp.Value);

            answer.AddRange(repeatedIdentifiers.OrderBy(y => y.Bib).ThenByDescending(z => z.WhenTouchedBinaryFormat));

            foreach (var repeat in answer) repeat.Comment = JghString.ConcatAsSentences(repeat.Comment, "Duplicate identifier.");

            return answer.ToArray();
        }

        private ParticipantHubItem[] DiagnoseDuplicateNames()
        {
            List<ParticipantHubItem> answer = [];

            JghListDictionary<string, ParticipantHubItem> listDictionaryGroupedByName = new();

            foreach (var item in _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers.Where(z => !z.MustDitchOriginatingItem))
                listDictionaryGroupedByName.Add(JghString.Concat(item.LastName, item.FirstName, item.MiddleInitial), item);

            List<ParticipantHubItem> repeatedNames = [];

            foreach (var nameKvp in listDictionaryGroupedByName)
                if (nameKvp.Value.Count > 1)
                    repeatedNames.AddRange(nameKvp.Value);

            answer.AddRange(repeatedNames.OrderBy(z => JghString.Concat(z.LastName, z.FirstName, z.MiddleInitial))
                .ThenByDescending(z => z.WhenTouchedBinaryFormat));

            foreach (var repeat in answer) repeat.Comment = "Duplicate person.";

            return answer.ToArray();
        }

        private Dictionary<string, ParticipantHubItem> ObtainMostRecentEntryForEachIdentifierOmittingDitchesAndDuplicatesOrderedByWhenTouched()
        {
            // for a contestant, find the mostRecentEntry of all entries. (The way the system is intended to work
            // this is the governing profile for the participant.) Although it may have to be modified for Race category.
            // At time of writing in July 2022, the only shift we want to take account of during the course of the season is to Race category.
            // Participants are entitled to change RaceGroup during the season. Also be aware that in real life there are myriad corrections
            // of wrong data or people changing RaceGroup before the first event or soon thereafter.

            var answer = new Dictionary<string, ParticipantHubItem>();

            var excludingDitches = _backingStoreGetYoungestDescendentOfEachOriginatingItemGuidIncludingDitchesAndDuplicateIdentifiers.Where(z => !z.MustDitchOriginatingItem).ToArray();

            var candidateDuplicatesGroupedByIdentifier = HubItemBase.ToListDictionaryGroupedByBib(excludingDitches);

            if (!candidateDuplicatesGroupedByIdentifier.Any()) return answer;

            foreach (var identifierKvp in candidateDuplicatesGroupedByIdentifier)
            {
                var entriesBelongingToThisIdentifier = identifierKvp.Value;

                var mostRecentEntryForThisIdentifier = entriesBelongingToThisIdentifier
                    .OrderBy(z => z.WhenTouchedBinaryFormat)
                    .LastOrDefault(); // take the most recent entry, crush the other entries.

                if (mostRecentEntryForThisIdentifier is null || mostRecentEntryForThisIdentifier.MustDitchOriginatingItem) 
                    continue; // if the most recent entry is a ditch, the contestant is non-existent. ignore this contestant.

                answer.Add(mostRecentEntryForThisIdentifier.Bib, mostRecentEntryForThisIdentifier);

            }

            return answer;
        }

        #endregion

    }
}